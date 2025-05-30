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
class MultiVectorDocumentIndexing:
    """
    A class to process PDFs from local or Azure,
    summarize their contents (texts, tables, and images), and
    store them in a retriever with multi-vector capability.
    """

    def __init__(
        self,
        llm: BaseLanguageModel,
        llm_multimodal: BaseLanguageModel, 
        vectorstore: VectorStore,
        store: BaseStore = InMemoryStore(),
        id_key: str = "doc_id",
    ):
        self.vectorstore = vectorstore
        self.store = store
        self.llm = llm
        self.llm_multimodal = llm_multimodal
        self.id_key = id_key

    def load_pdf(self, path: str = None, azure_blob: Optional[dict] = None) -> str:
        """
        Load a PDF file from local path or Azure Blob Storage.

        Args:
            path (Optional[str]): Local file path.
            azure_blob (Optional[dict]): Dictionary with keys `azure_blob_conn_str`, `container`, and `blob_pdf`.

        Returns:
            str: Path to the downloaded or existing PDF.
        """
        if path:
            return path

        # TODO: implement azure load with tempfile

    def split_pdf(self, file_path: str):
        """
        Partition PDF into chunks and separate by type.

        Args:
            file_path (str): Path to the PDF.

        Returns:
            tuple: Lists of texts, tables, and base64-encoded images.
        """
        # Reference: https://docs.unstructured.io/open-source/core-functionality/chunking
        chunks = partition_pdf(
            filename=file_path,
            infer_table_structure=True,            # extract tables
            strategy="hi_res",                     # mandatory to infer tables

            extract_image_block_types=["Image"],   # Add 'Table' to list to extract image of tables
            # image_output_dir_path=output_path,   # if None, images and tables will saved in base64

            extract_image_block_to_payload=True,   # if true, will extract base64 for API usage

            chunking_strategy="by_title",          # or 'basic'
            max_characters=10000,                  # defaults to 500
            combine_text_under_n_chars=2000,       # defaults to 0
            new_after_n_chars=6000,
        )

        # We get 2 types of elements from the partition_pdf function
        texts, tables, images_b64 = [], [], []

        for chunk in chunks:
            if "Table" in str(type(chunk)):
                tables.append(chunk)

            if "CompositeElement" in str(type(chunk)):
                texts.append(chunk)
                for el in chunk.metadata.orig_elements:
                    if "Image" in str(type(el)):
                        images_b64.append(el.metadata.image_base64)

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
        Executes a `.batch()` call with automatic retries in case of HTTP errors,
        particularly useful for handling rate limits (HTTP 429 errors).

        Args:
            chain (RunnableSequence): A LangChain runnable object, such as a summarization chain.
            inputs (list[Any]): A list of input elements to process in batch.
            config (Optional[dict[str, Any]]): Configuration options for the batch run 
                                            (e.g., {"max_concurrency": 3}). Optional.

        Returns:
            list[Any]: The list of results returned by the batch execution.
        """
        return chain.batch(inputs, config)
    
    def summarize_elements(self, texts: list, tables: list, images: list):
        """
        Summarizes text, tables, and images separately.

        Args:
            texts (list): CompositeElement objects.
            tables (list): TableElement objects.
            images (list): base64 strings.

        Returns:
            tuple: summaries of text, tables, and images.
        """

        summarize_chain = self._get_text_table_summary_chain()
        table_html = [table.metadata.text_as_html for table in tables]

        # Retry-enhanced batch calls
        text_summaries = self._retry_batch(summarize_chain, texts)
        table_summaries = self._retry_batch(summarize_chain, table_html)

        image_chain = self._get_image_summary_chain()
        formatted_imgs = [{"image": b64} for b64 in images]
        image_summaries = self._retry_batch(image_chain, formatted_imgs, config={})

        return text_summaries, table_summaries, image_summaries

    def embed_store_documents(
        self,
        chunks_dicts: dict[str, tuple[list, list]],
        metadata: Optional[list[dict[str, Any]]] = None,
        metadata_retriever: Optional[dict[str, Any]] = None
    ) -> MultiVectorRetriever:
        """
        Embed and store all chunks into the retriever.

        Args:
            chunks_dicts (dict): Dictionary where each value is a tuple (chunks_list, summaries_list).
            metadata (dict, optional): Metadata for each chunk.
            metadata_retriever (dict, optional): Metadata for retriever.

        Returns:
            MultiVectorRetriever: Ready-to-query retriever.
        """
        retriever = MultiVectorRetriever(
            vectorstore=self.vectorstore,
            docstore=self.store,
            id_key=self.id_key,
            metadata=metadata_retriever
        )

        for content_type, (chunk_list, summaries_list) in chunks_dicts.items():
            # TODO: logs content_type processing and metadata_list in the chunks_dicts
            if chunk_list and summaries_list and len(chunk_list) == len(summaries_list):
                chunk_ids = [str(uuid.uuid4()) for _ in chunk_list]
                summary_docs = [
                    Document(page_content=summaries_list[i], metadata={self.id_key: chunk_ids[i], **(metadata or {})})
                    for i in range(len(summaries_list))
                ]
                retriever.vectorstore.add_documents(summary_docs)
                retriever.docstore.mset(list(zip(chunk_ids, chunk_list)))

        return retriever