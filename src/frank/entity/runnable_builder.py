from abc import ABC, abstractmethod
from typing import List, Optional, Any
from pydantic import BaseModel
from langchain_core.runnables import Runnable
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain.vectorstores import VectorStore
from langchain_core.tools import BaseTool


class RunnableBuilder(ABC):
    def __init__(
        self,
        model: BaseLanguageModel,
        vectordb: Optional[VectorStore] = None,
        tools: Optional[List[BaseTool]] = None,
        structured_output_schema: Optional[BaseModel] = None,
    ):
        self.model = model
        self.vectordb = vectordb
        self.tools = tools
        self.structured_output_schema = structured_output_schema

        # Start the runnable
        self._runnable: Runnable = None
        self._retriever: Optional[BaseRetriever] = None
    
    def _build_prompt(self) -> ChatPromptTemplate:
        """
        Build the prompt runnable chain and return it.
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not implement `_build_prompt`.")
    
    def _build_retriever(self, **kwargs: Any) -> BaseRetriever:
        """
        Builds and returns a retriever from the vectorstore.
        Subclasses can override this for custom logic.
        """
        if self.vectordb is None:
            raise ValueError(f"{self.__class__.__name__} cannot build a retriever because `vectordb` is None.")
        return self.vectordb.as_retriever(**kwargs)

    @abstractmethod
    def _configure_runnable(self) -> Runnable:
        """
        Configure the main runnable and return it. It could be a chain or a retriever.
        """
        pass
    
    @property
    def _get_runnable(self) -> Runnable:
        """
        Lazily initialize and return the configured runnable.
        """
        if self._runnable is None:
            self._runnable = self._configure_runnable()
        return self._runnable
    
    @property
    def _get_retriever(self) -> BaseRetriever:
        """
        Lazily initialize and return the configured retriever.
        """
        if self._retriever is None:
            self._retriever = self._build_retriever()
        return self._retriever

    def invoke(self, input: Any) -> Any:
        """
        Invoke the runnable.
        """
        return self._get_runnable.invoke(input)


    def ainvoke(self, input: Any) -> Any:
        """
        Ainvoke the runnable.
        """
        return self._get_runnable.ainvoke(input)
    
    def get(self) -> Runnable:
        """
        Return the configured runnable.
        """
        return self._get_runnable

    def get_raw_retriever(self) -> BaseRetriever:
        """
        Returns the base retriever
        """
        return self._get_retriever
