from langchain.vectorstores import VectorStore
from langchain_core.retrievers import BaseRetriever

from langchain_core.language_models import BaseLanguageModel
from core.utils.rag.langchain_unstructured import LangChainMultiVectorDocumentIndexing

class LocalMultiVectorRetriever:
    def __init__(self, llm: BaseLanguageModel, llm_multimodal: BaseLanguageModel, vectordb: VectorStore):
        self.llm = llm
        self.llm_multimodal = llm_multimodal
        self.vectordb = vectordb
        self.retriever = None 

    def indexing_pdf(self, pdf_path: str) -> None:
        # Load, split, summarize, and embed documents
        indexing = LangChainMultiVectorDocumentIndexing(
            llm=self.llm, 
            llm_multimodal=self.llm_multimodal, 
            vectorstore=self.vectordb
        )
        
        indexing.load_pdf(pdf_path)
        indexing.split_pdf()
        indexing.summarize_elements()
        indexing.embed_store_documents()

        # Configuramos el retriever directamente como un atributo de la clase
        self.retriever = indexing.get_retriever()

    def get_retriever(self) -> BaseRetriever:
        if self.retriever is None:
            raise ValueError("Index local no ha sido inicializado. Asegúrate de llamar a indexing_pdf() primero.")