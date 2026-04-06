import logging
from langchain_core.runnables import RunnableLambda
from langchain_core.retrievers import BaseRetriever
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable

from frank.entity.runnable_builder import RunnableBuilder
from core_examples.utils.rag.processing import parse_docs, parse_context


class MultimodalRetriever(RunnableBuilder):
    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])

    def __init__(self, model: BaseLanguageModel, retriever: BaseRetriever) -> None:
        """Compose a multimodal retrieval runnable from a pre-built retriever."""

        super().__init__(model=model, retriever=retriever)

        self.logger.info("MultimodalRetriever initialized")

    def _configure_runnable(self) -> Runnable:
        """Compose retriever output parsing into the runnable returned by invoke or ainvoke."""

        if self.retriever is None:
            raise ValueError("MultimodalRetriever requires a pre-built retriever.")

        retriever = self.retriever
        multimodal_retriever_parse_chain = retriever | RunnableLambda(parse_docs) | RunnableLambda(parse_context)

        return multimodal_retriever_parse_chain