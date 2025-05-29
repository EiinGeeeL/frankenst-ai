import uuid
import asyncio
from typing import Optional, Callable, Dict, Any

from unstructured.partition.pdf import partition_pdf
from langchain.schema.document import Document
from langchain.vectorstores import VectorStore
from langchain_core.stores import BaseStore
from langchain.storage import InMemoryStore
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.multi_vector import MultiVectorRetriever


class MultiVectorDocumentIndexing:
    """
    A class to process PDFs from local or Azure Blob Storage,
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

    async def load_pdf(self, path: str = None, azure_blob: Optional[dict] = None) -> str:
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

        # TODO: implement azure load
        # if azure_blob:
        #     blob_service_client = BlobServiceClient.from_connection_string(
        #         azure_blob["azure_blob_conn_str"]
        #     )
        #     blob_client = blob_service_client.get_blob_client(
        #         container=azure_blob["container"],
        #         blob=path
        #     )
        #     pdf_data = blob_client.download_blob().readall()
        #     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        #         temp_file.write(pdf_data)
        #         return temp_file.name

        # raise ValueError("Must provide either `path` or `azure_blob`.")

    async def split_pdf(self, file_path: str):
        """
        Partition PDF into chunks and separate by type.

        Args:
            file_path (str): Path to the PDF.

        Returns:
            tuple: Lists of texts, tables, and base64-encoded images.
        """
        chunks = partition_pdf(
            filename=file_path,
            infer_table_structure=True,            # extract tables
            strategy="hi_res",                     # mandatory to infer tables
            extract_image_block_types=["Image"],   # Add 'Table' to list to extract image of tables
            extract_image_block_to_payload=True,   # if true, will extract base64 for API usage
            chunking_strategy="by_title",          # or 'basic'
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

        return texts, tables, images_b64

    def _get_text_table_summary_chain(self):
        prompt_text = """
        Eres un asistente encargado de resumir tablas y textos.
        Proporciona un resumen conciso de la tabla o texto.

        Responde solo con el resumen, sin comentarios adicionales.
        No comiences tu mensaje diciendo "Aquí hay un resumen" o algo similar.
        Simplemente proporciona el resumen tal cual.

        Tabla o fragmento de texto: {element}
        """
        prompt = ChatPromptTemplate.from_template(prompt_text)
        return {"element": lambda x: x} | prompt | self.llm | StrOutputParser()

    def _get_image_summary_chain(self):
        prompt_text = """Describe the image in detail. For context,
                      the image is part of a research paper explaining the transformers
                      architecture. Be specific about graphs, such as bar plots."""
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

    async def summarize_elements(self, texts: list, tables: list, images: list):
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

        text_summaries, table_summaries, image_summaries = await asyncio.gather(
            asyncio.to_thread(summarize_chain.batch, texts, {"max_concurrency": 3}),
            asyncio.to_thread(summarize_chain.batch, table_html, {"max_concurrency": 3}),
            asyncio.to_thread(
                self._get_image_summary_chain().batch,
                [{"image": b64} for b64 in images],
            ),
        )

        return text_summaries, table_summaries, image_summaries

    def embed_store_documents(
        self,
        texts: list,
        text_summaries: list,
        tables: list,
        table_summaries: list,
        images: list,
        image_summaries: list,
        metadata_fn: Optional[Callable[[Any], Dict[str, Any]]] = None,
    ) -> MultiVectorRetriever:
        """
        Index all elements into the retriever.

        Args:
            texts (list): CompositeElement objects.
            text_summaries (list): List of text summaries.
            tables (list): TableElement objects.
            table_summaries (list): List of table summaries.
            images (list): Base64 strings.
            image_summaries (list): List of image summaries.
            metadata_fn (Callable): Optional function to generate additional metadata from the original element.

        Returns:
            MultiVectorRetriever: Ready-to-query retriever.
        """
        retriever = MultiVectorRetriever(
            vectorstore=self.vectorstore,
            docstore=self.store,
            id_key=self.id_key,
        )

        # Add texts
        doc_ids = [str(uuid.uuid4()) for _ in texts]
        summary_texts = [
            Document(
                page_content=summary,
                metadata={self.id_key: doc_ids[i], **(metadata_fn(texts[i]) if metadata_fn else {})},
            )
            for i, summary in enumerate(text_summaries)
        ]
        retriever.vectorstore.add_documents(summary_texts)
        retriever.docstore.mset(list(zip(doc_ids, texts)))

        # Add tables
        table_ids = [str(uuid.uuid4()) for _ in tables]
        summary_tables = [
            Document(
                page_content=summary,
                metadata={self.id_key: table_ids[i], **(metadata_fn(tables[i]) if metadata_fn else {})},
            )
            for i, summary in enumerate(table_summaries)
        ]
        retriever.vectorstore.add_documents(summary_tables)
        retriever.docstore.mset(list(zip(table_ids, tables)))

        # Add images
        img_ids = [str(uuid.uuid4()) for _ in images]
        summary_img = [
            Document(
                page_content=summary,
                metadata={self.id_key: img_ids[i], **(metadata_fn(images[i]) if metadata_fn else {})},
            )
            for i, summary in enumerate(image_summaries)
        ]
        retriever.vectorstore.add_documents(summary_img)
        retriever.docstore.mset(list(zip(img_ids, images)))

        return retriever
