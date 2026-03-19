from typing import List
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from services.ai_foundry.llm import LLMServices
from core.components.retrievers.ai_search_simple_semantic_retriever.ai_search_simple_semantic_retriever import AISearchSimpleSemanticRetriever
from core.utils.key_vault import get_secret

class RetrieverTeradataSchemas:
    @staticmethod
    def run(query: str) -> List:
        """
        Esta herramienta transforma una consulta en lenguaje natural en un vector y recupera contexto del contenido y los esquemas de una base de datos, Teradata.
    
        Args:
            query (str): Pregunta o consulta en lenguaje natural sobre la base de datos Teradata.

        Returns:
            str: Lista con los documentos y esquemas más relevantes que contiene la base de datos Teradata.
        """
        
        LLMServices.launch()
   
        # Create search client
        service_endpoint = get_secret("AZURE_SEARCH_SERVICE_ENDPOINT")
        key = get_secret("AZURE_SEARCH_API_KEY")
        index_name = "pokeseriex-index"
        search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
        
        # Use the retriever
        retriever = AISearchSimpleSemanticRetriever(search_client=search_client, emmbeddings=LLMServices.embeddings)

        results = retriever.retrieve(query)
        return results