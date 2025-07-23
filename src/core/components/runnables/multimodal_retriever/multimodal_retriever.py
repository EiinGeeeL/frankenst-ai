import logging
from langchain_core.runnables import RunnableLambda
from langchain_core.retrievers import BaseRetriever
from langchain.vectorstores import VectorStore
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable

from frank.entity.runnable_builder import RunnableBuilder
from core.utils.rag.langchain_unstructured import LangChainMultiVectorDocumentIndexing
from core.utils.rag.processing import parse_docs, parse_context


class MultimodalRetriever(RunnableBuilder):
    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])

    def __init__(self, model: BaseLanguageModel, vectordb: VectorStore):
        super().__init__(model=model, vectordb=vectordb)

        self.logger.info("MultimodalRetriever initialized")

    def _build_retriever(self) -> BaseRetriever:

        # Index phase
        indexing = LangChainMultiVectorDocumentIndexing(llm=self.model, llm_multimodal=self.model, vectorstore=self.vectordb)

        indexing.load_pdf('artifacts/rag_docs/EP003 - Ash Catches a Pokémon.pdf')
        indexing.split_pdf()
        indexing.summarize_elements()
        indexing.embed_store_documents()
        retriever = indexing.get_retriever()

        return retriever

    def _configure_runnable(self) -> Runnable:
        
        # prepare for retrieve multimodal context
        retriever = self._get_retriever
        multimodal_retriever_parse_chain = retriever | RunnableLambda(parse_docs) | RunnableLambda(parse_context)

        return multimodal_retriever_parse_chain