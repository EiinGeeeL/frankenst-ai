from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from services.foundry.llms import LLMServices
from core_examples.utils.rag.ai_search_unstructured_indexer import AISearchIndexManager, AISearchMultiVectorDocumentIndexer
from core_examples.utils.key_vault import get_secret
from core_examples.utils.blob_storage import download_pdf_from_blob, parse_blob_subject


class Orchestrator:
    @staticmethod
    def check_index(index_name: str):

        # Initialize index client
        service_endpoint = get_secret("AZURE_SEARCH_SERVICE_ENDPOINT")
        key = get_secret("AZURE_SEARCH_API_KEY")
        index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

        # Initialize ai_search_index_manager
        ai_search_index_manager = AISearchIndexManager(index_name=index_name, index_client=index_client)

        if not ai_search_index_manager.index_exists():
            # Create index
            ai_search_index_manager.create_index()
    
    @staticmethod        
    def document_indexing(index_name: str, subject: str):
    
        # Initialize search client
        service_endpoint = get_secret("AZURE_SEARCH_SERVICE_ENDPOINT")
        key = get_secret("AZURE_SEARCH_API_KEY")
        search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

        # Parse the subject
        blob_path, container_name = parse_blob_subject(subject=subject)
        filename = blob_path.split("/")[-1]

        # Load file from blob
        temp_filepath = download_pdf_from_blob(blob_path=blob_path, container_name=container_name)

        # Prepare the document
        LLMServices.launch()
 
        # Initialize indexer
        indexer =  AISearchMultiVectorDocumentIndexer(search_client, LLMServices.model, LLMServices.embeddings)

        if filename.endswith('.pdf'):
            indexer.load_pdf(temp_filepath)
            indexer.split_pdf()
            indexer.summarize_elements()
            indexer.embed_ai_search_index_documents()
            indexer.upload_documents()
        else:
            raise ValueError("Provide a pdf file")

    @staticmethod        
    def delete_document_by_filename(index_name: str, subject: str):

        # Initialize search client
        service_endpoint = get_secret("AZURE_SEARCH_SERVICE_ENDPOINT")
        key = get_secret("AZURE_SEARCH_API_KEY")
        search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

        # Parse the subject
        blob_path, _ = parse_blob_subject(subject=subject)
        filename = blob_path.split("/")[-1]

        # Initialize ai_search_index_manager
        indexer =  AISearchMultiVectorDocumentIndexer(search_client)
        indexer.delete_document_by_filename(filename=filename)