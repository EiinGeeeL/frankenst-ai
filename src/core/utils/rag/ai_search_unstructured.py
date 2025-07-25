import os
import uuid
import datetime as dt
from typing import Optional, Any, Dict, List, Union
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from unstructured.partition.pdf import partition_pdf

from azure.core.exceptions import HttpResponseError
from azure.search.documents import SearchClient
from azure.search.documents.models import IndexingResult, VectorizedQuery
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType,
    SearchField, VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
    SemanticConfiguration, SemanticPrioritizedFields, SemanticField,
    SemanticSearch, ComplexField, CorsOptions, ScoringProfile
)


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel
from langchain_core.embeddings import Embeddings
from langchain_core.runnables.base import RunnableSequence

class AISearchMultiVectorDocumentIndexing:
    """
    A class to process PDFs (local or cloud), split content into chunks (texts, tables, images),
    summarize them, embed and store them in a retriever with multi-vector capability.
    Maintains internal state for elements, summaries, and chunks for later retrieval or debugging.
    """

    def __init__(
        self,
        llm_multimodal: BaseLanguageModel,
        embeddings: Embeddings,
        search_client: SearchClient,
    ):
        """
        Initializes the MultiVectorDocumentIndexing pipeline.

        Args:
            llm_multimodal (BaseLanguageModel): Multimodal model for summarizing text, tables and images.
            embeddings (Embeddings): An embedding model used to generate vectors.
        search_client (SearchClient): Azure AI Search client used to upload in a index the processed documents.

        """
        self.llm_multimodal = llm_multimodal
        self.embeddings = embeddings
        self.search_client = search_client

        # Internal state
        self.file_path: Optional[str] = None
        self.elements: dict[str, list] = {"texts": [], "tables": [], "images": []}
        self.summaries: dict[str, list] = {"texts": [], "tables": [], "images": []}
        self.documents: List[dict] = []


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
            
            elif "CompositeElement" in str(type(chunk)):
                has_table = False
                for el in chunk.metadata.orig_elements:
                    if "Table" in str(type(el)):
                        has_table = True
                    if "Image" in str(type(el)):
                        images_b64.append(el.metadata.image_base64)
                
                if has_table:
                    tables.append(chunk)
                else:
                    texts.append(chunk)

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
        return {"element": lambda x: x} | prompt | self.llm_multimodal | StrOutputParser()

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

        formatted_table_html = [t.text + t.metadata.text_as_html for t in self.elements["tables"]] # ad to the table formatted to the text
        formatted_imgs = [{"image": b64} for b64 in self.elements["images"]]

        text_summaries = self._retry_batch(summarize_chain, self.elements["texts"]) # text already obtain as str the text
        table_summaries = self._retry_batch(summarize_chain, formatted_table_html)
        image_summaries = self._retry_batch(image_chain, formatted_imgs, config={})

        self.summaries = {
            "texts": text_summaries,
            "tables": table_summaries,
            "images": image_summaries
        }

        return text_summaries, table_summaries, image_summaries

    def embed_ai_search_index_documents(self) -> List[Dict[str, Any]]:
        documents = []
        
        for content_type in ["texts", "tables", "images"]:
            chunks_list = self.elements.get(content_type)
            summaries_list = self.summaries.get(content_type)
            embeddings_summaries_list = self.embeddings.embed_documents(summaries_list)

            if chunks_list and summaries_list and len(chunks_list) == len(summaries_list):
                for i, chunk in enumerate(chunks_list):
                    doc_id = str(uuid.uuid4())
                    doc_type = content_type
                    summary = summaries_list[i]
                    embeddings_summary = embeddings_summaries_list[i]

                    # Metadatos opcionales
                    try:
                        metadata = {
                            "languages": ",".join(getattr(chunk.metadata, "languages", ["und"])),
                            "last_modified": dt.datetime.now(dt.UTC),
                            "page_number": getattr(chunk.metadata, "page_number", 1),
                            "file_directory": getattr(chunk.metadata, "file_directory", None),
                            "filename": getattr(chunk.metadata, "filename", None),
                            "filetype": getattr(chunk.metadata, "filetype", None),
                            "uri": f"https://www.devops.wiki/{getattr(chunk.metadata, "filename", None)}" # TODO: improve dinamic url
                        }
                        # Eliminar claves con valor None
                        metadata = {k: v for k, v in metadata.items() if v is not None}
                    except Exception:
                        pass

                    document = {
                        "id": doc_id,
                        "type": doc_type,
                        "summary": summary,
                        "content": str(chunk),  # puede ser string (texto/base64) o estructura table
                        "metadata": metadata,
                        "embeddings": embeddings_summary,
                    }
                    documents.append(document)

        self.documents = documents

        return documents
    
    def upload_documents(self) -> List[IndexingResult]:
        return self.search_client.upload_documents(documents=self.documents)


class AISearchIndexManager:
    """
    Manages the lifecycle and configuration of an Azure Cognitive Search index, 
    including creation, updating, deletion, and retrieval of the index definition.
    """

    def __init__(self, index_name: str, index_client: SearchIndexClient):
        """
        Initializes the AISearchIndexManager.

        Args:
            index_name (str): The name of the index to manage.
            index_client (SearchIndexClient): The Azure SearchIndexClient to interact with the service.
        """
        self.index_name = index_name
        self.index_client = index_client

    def create_index(self, search_field: List[Union[SearchField, SimpleField, SearchableField, ComplexField]] = None):
        """
        Creates a new search index if it does not already exist.

        Args:
            search_field (SearchField, optional): Custom field definition for the index. 
                If not provided, a default set of fields is used.

        Raises:
            Exception: If the index already exists.
        """
        if self.index_name not in [idx.name for idx in self.index_client.list_indexes()]:
            index = SearchIndex(
                name=self.index_name,
                fields=self._get_basic_fields() if not search_field else search_field,
                vector_search=self._get_vector_search_config(),
                semantic_search=self._get_semantic_search_config(),
                cors_options=CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
            )
            self.index_client.create_index(index)
        else:
            raise Exception(f"The index '{self.index_name}' already exists. Please update it instead.")

    def get_index(self):
        """
        Retrieves the definition of the current index.

        Returns:
            SearchIndex: The current index definition.
        """
        return self.index_client.get_index(name=self.index_name)

    def update_index(self, search_field: List[Union[SearchField, SimpleField, SearchableField, ComplexField]] = None):
        """
        Updates an existing index with new field definitions or scoring profiles.

        Args:
            search_field (SearchField, optional): Custom field definition for the index. 
                If not provided, the default fields are used.
        """
        scoring_profile = ScoringProfile(name="MyProfile")

        index = SearchIndex(
            name=self.index_name,
            fields=self._get_basic_fields() if not search_field else search_field,
            scoring_profiles=[scoring_profile],
            cors_options=CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        )

        self.index_client.create_or_update_index(index=index)

    def delete_index(self):
        """
        Deletes the current search index.
        """
        self.index_client.delete_index(self.index_name)

    def _get_basic_fields(self) -> List[Union[SearchField, SimpleField, SearchableField, ComplexField]]:
        """
        Returns the default set of fields used for semantic embedding and vector search.

        Returns:
            list[SearchField]: A list of predefined search fields.
        """
        return [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="type", type=SearchFieldDataType.String, filterable=True, sortable=True, searchable=False),
            SearchableField(name="content", type=SearchFieldDataType.String, searchable=False),
            SearchableField(name="summary", type=SearchFieldDataType.String, searchable=False),
            ComplexField(name="metadata", fields=[
                SimpleField(name="filetype", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="languages", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="last_modified", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
                SimpleField(name="page_number", type=SearchFieldDataType.Int32, filterable=True),
                SimpleField(name="file_directory", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="filename", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="uri", type=SearchFieldDataType.String, filterable=True),
            ]),
            SearchField(
                name="embeddings",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=1536,
                vector_search_profile_name="perfilHnsw"
            )
        ]

    def _get_vector_search_config(self) -> VectorSearch:
        """
        Returns the HNSW vector search configuration.
        """
        return VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
            profiles=[VectorSearchProfile(name="perfilHnsw", algorithm_configuration_name="hnsw")]
        )

    def _get_semantic_search_config(self) -> SemanticSearch:
        """
        Returns the semantic search configuration.
        """
        semantic_config = SemanticConfiguration(
            name="default",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content")]
            )
        )
        return SemanticSearch(configurations=[semantic_config])

class AISearchMultiVectorRetriever:
    def __init__(
        self,
        embeddings: Embeddings,
        search_client: SearchClient
    ):
        """
        Args:
            embeddings: Model used to generate query embeddings.
            search_client: Azure Search client configured with endpoint, index, and credentials.
        """
        self.embeddings = embeddings
        self.search_client = search_client

    def _search(self, query: str, k: int = 5) -> List[dict]:
        """Performs a vector search with the given query."""
        vector = self.embeddings.embed_query(query)

        vector_query = VectorizedQuery(
            vector=vector,
            kind="vector",
            fields="embeddings",
            k_nearest_neighbors=k,
            exhaustive=True,
            weight=0.5,
        )

        results = self.search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=["type", "content", "metadata"],
            include_total_count=True,
            top=k # max documents retrievers
        )

        return list(results)

    def _parse_results(self, results: List[dict], metadata_as_content: bool = False) -> Dict[str, List[str]]:
        """Groups documents by type, optionally appending metadata to content."""
        grouped = {"texts": [], "images": []}
        for doc in results:
            t = doc.get("type")
            c = doc.get("content", "")
            
            if metadata_as_content:
                metadata = doc.get("metadata")
                if metadata:
                    c += f"\n\nMetadata: {metadata}"

            if t == "texts" or t == "tables":
                grouped["texts"].append(c)
            elif t == "images":
                grouped["images"].append(c)

        return grouped


    def get_context(self, query: str, k: int = 5) -> Dict[str, object]:
        """
        Performs the search and builds the context.

        Returns:
            dict with keys "texts" (concatenated string) and "images" (list of dicts for prompt).
        """
        results = self._search(query, k)
        docs_by_type = self._parse_results(results)

        context_text = "\n".join(docs_by_type.get("texts", []))

        context_images = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img}"}
            }
            for img in docs_by_type.get("images", [])
        ]

        return {
            "texts": context_text.strip(),
            "images": context_images
        }
