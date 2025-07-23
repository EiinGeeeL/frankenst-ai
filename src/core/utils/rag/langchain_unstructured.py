import os
import tempfile
import uuid
from typing import Optional, Any

from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from unstructured.partition.pdf import partition_pdf
from azure.core.exceptions import HttpResponseError
from langchain.schema.document import Document
from langchain.vectorstores import VectorStore
from langchain_core.stores import BaseStore
from langchain.storage import InMemoryStore
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.base import RunnableSequence
from langchain.retrievers.multi_vector import MultiVectorRetriever

# TODO: Async load, split, summary
# TODO: metadata list to impement unstructured
# TODO: load folder and more than one file
# TODO: externalizate the context
# TODO: add the logic in the slip to exclude small images (icons)
class LangChainMultiVectorDocumentIndexing:
    """
    A class to process PDFs (local or cloud), split content into chunks (texts, tables, images),
    summarize them, embed and store them in a retriever with multi-vector capability.
    Maintains internal state for elements, summaries, and chunks for later retrieval or debugging.
    """

    def __init__(
        self,
        llm: BaseLanguageModel,
        llm_multimodal: BaseLanguageModel,
        vectorstore: VectorStore,
        store: BaseStore = InMemoryStore(),
        id_key: str = "doc_id",
        metadata_retriever: Optional[dict] = None
    ):
        """
        Initializes the MultiVectorDocumentIndexing pipeline.

        Args:
            llm (BaseLanguageModel): Language model for summarizing text and tables.
            llm_multimodal (BaseLanguageModel): Multimodal model for summarizing images.
            vectorstore (VectorStore): Vector store to store and retrieve embeddings.
            store (BaseStore): Document store for full chunk content.
            id_key (str): Key for identifying documents.
            metadata_retriever (dict, optional): Metadata to attach to the retriever.
        """
        self.llm = llm
        self.llm_multimodal = llm_multimodal
        self.vectorstore = vectorstore
        self.store = store
        self.id_key = id_key
        self.metadata_retriever = metadata_retriever

        # Internal state
        self.retriever: Optional[MultiVectorRetriever] = None
        self.file_path: Optional[str] = None
        self.elements: dict[str, list] = {"texts": [], "tables": [], "images": []}
        self.summaries: dict[str, list] = {"texts": [], "tables": [], "images": []}

        self._init_retriever()

    def _init_retriever(self):
        """Initializes the internal MultiVectorRetriever."""
        self.retriever = MultiVectorRetriever(
            vectorstore=self.vectorstore,
            docstore=self.store,
            id_key=self.id_key,
            metadata=self.metadata_retriever,
        )

    def load_pdf(self, path: str = None, azure_blob: Optional[dict] = None) -> None:
        """
        Loads a PDF file from a local path or Azure Blob Storage.

        Args:
            path (str): Local file path.
            azure_blob (dict, optional): Azure blob config.

        Raises:
            ValueError: If neither path nor azure_blob is provided.
        """
        if path and not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        elif path:
            self.file_path = path
        elif azure_blob:
            raise NotImplementedError("Azure blob loading is not yet implemented.")
        else:
            raise ValueError("Provide a path or azure_blob info.")

    def split_pdf(self, min_image_size_filter: tuple = None):
        """
        Splits the loaded PDF into texts, tables, and base64-encoded images.
        Updates internal state.

        Args:
            min_image_size_filter (tuple): (width, height) size below which images will be filtered out.

        Returns:
            tuple: Lists of texts, tables, and images.
        """
        chunks = partition_pdf(
            filename=self.file_path,
            infer_table_structure=True,
            strategy="hi_res",
            extract_image_block_types=["Image"],
            extract_image_block_to_payload=True,
            chunking_strategy="by_title",
            max_characters=10000,
            combine_text_under_n_chars=2000,
            new_after_n_chars=6000,
        )

        texts, tables, images_b64 = [], [], []

        for chunk in chunks:
            if "Table" in str(type(chunk)):
                tables.append(chunk)
            if "CompositeElement" in str(type(chunk)):
                texts.append(chunk)
                for el in chunk.metadata.orig_elements:
                    if "Image" in str(type(el)):
                        images_b64.append(el.metadata.image_base64)

        self.elements = {
            "texts": texts, 
            "tables": tables, 
            "images": images_b64
            }
        
        return texts, tables, images_b64

    def _get_text_table_summary_chain(self):
        prompt_text = """
        You are an assistant in charge of summarizing tables and text.

        Provide a concise summary of the table or text.

        Reply with only the summary, without additional comments.
        Do not begin your message by saying "Here's a summary" or something similar.
        Simply provide the summary as is.

        Table or text fragment: {element}
        """
        prompt = ChatPromptTemplate.from_template(prompt_text)
        return {"element": lambda x: x} | prompt | self.llm | StrOutputParser()

    def _get_image_summary_chain(self):
        prompt_text = """
        Describe the image in detail. 
        """

        messages = [
            (
                "user",
                [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64,{image}"},
                    },
                ],
            )
        ]
        prompt = ChatPromptTemplate.from_messages(messages)
        return prompt | self.llm_multimodal | StrOutputParser()

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(HttpResponseError),
        reraise=True
    )
    def _retry_batch(
        self,
        chain: RunnableSequence,
        inputs: list[Any],
        config: Optional[dict[str, Any]] = {"max_concurrency": 3}
    ) -> list[Any]:
        """
        Executes a `.batch()` call with retry on HTTP 429 or transient errors.

        Args:
            chain (RunnableSequence): Runnable chain to execute.
            inputs (list): Inputs to pass in batch.
            config (dict, optional): Execution config (e.g., concurrency).

        Returns:
            list: Results from batch execution.
        """
        return chain.batch(inputs, config)

    def summarize_elements(self):
        """
        Summarizes the elements (texts, tables, images) extracted from the PDF.
        Updates internal state.

        Returns:
            tuple: Lists of summaries for texts, tables, and images.
        """
        summarize_chain = self._get_text_table_summary_chain()
        image_chain = self._get_image_summary_chain()

        table_html = [t.metadata.text_as_html for t in self.elements["tables"]]
        formatted_imgs = [{"image": b64} for b64 in self.elements["images"]]

        text_summaries = self._retry_batch(summarize_chain, self.elements["texts"])
        table_summaries = self._retry_batch(summarize_chain, table_html)
        image_summaries = self._retry_batch(image_chain, formatted_imgs, config={})

        self.summaries = {
            "texts": text_summaries,
            "tables": table_summaries,
            "images": image_summaries
        }

        return text_summaries, table_summaries, image_summaries

    def embed_store_documents(self):
        """
        Embeds and stores all elements with their summaries into the retriever.
        Updated the retriever state
        """
        for content_type in ["texts", "tables", "images"]:
            chunks_list = self.elements[content_type]
            summaries_list = self.summaries[content_type]
            if chunks_list and summaries_list and len(chunks_list) == len(summaries_list):
                chunk_ids = [str(uuid.uuid4()) for _ in chunks_list]
                summary_docs = [
                    Document(page_content=summaries_list[i], metadata={self.id_key: chunk_ids[i]})
                    for i in range(len(summaries_list))
                ]
                self.retriever.vectorstore.add_documents(summary_docs)
                self.retriever.docstore.mset(list(zip(chunk_ids, chunks_list)))


    def get_retriever(self) -> MultiVectorRetriever:
        """
        Returns the retriever populated during the workflow.

        Returns:
            MultiVectorRetriever: Ready-to-query retriever.
        """

        if any(self.elements['texts']) or any(self.summaries['texts']):
            return self.retriever
        else:
            raise ValueError("Not chunks detected. If already exist in store/vectorstore please use get_prebuild_retriever.")
    
    def get_prebuilt_retriever(self) -> MultiVectorRetriever:
        """
        Returns an existing retriever assuming documents already exist in store/vectorstore.

        Returns:
            MultiVectorRetriever: The retriever ready for querying.
        """

        return self.retriever