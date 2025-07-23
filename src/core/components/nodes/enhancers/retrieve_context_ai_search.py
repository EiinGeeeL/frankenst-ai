import os
from typing import Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from langchain_core.embeddings import Embeddings
from frank.entity.statehandler import StateEnhancer
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from core.utils.rag.ai_search_unstructured import AISearchMultiVectorRetriever


class RetrieveContextAISearch(StateEnhancer):
    """Retrieve context."""
    async def enhance(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> dict[str, list]: 
        
        if "iterations" in state and state.get("iterations", 0) > 0:
            question = state["question"]
        else:
            question = state["messages"][-1].content

        if not isinstance(self.embeddings, Embeddings):
            raise TypeError("Expected 'embeddings' to be an instance of langchain_core.embeddings.Embeddings")
        
        search_client = SearchClient(endpoint=os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT"), index_name="demo-rag-multimodal-index", credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY")))
        retriever = AISearchMultiVectorRetriever(embeddings=self.embeddings, search_client=search_client)

        retrieved_docs_context = retriever.get_context(question)

        return {"context": retrieved_docs_context, "question": question}