from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
from langchain_core.runnables import Runnable
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
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

        # Start the chain
        self._chain: Runnable = None
    
    @abstractmethod
    def _build_prompt(self) -> ChatPromptTemplate:
        """
        Build the prompt chain and return it.
        """
        pass

    @abstractmethod
    def _configure_chain(self) -> Runnable:
        """
        Configure the main chain and return it.
        """
        pass
    
    @property
    def _get_chain(self) -> Runnable:
        """
        Lazily initialize and return the configured chain.
        """
        if self._chain is None:
            self._chain = self._configure_chain()
        return self._chain


    def invoke(self, message: str) -> str:
        """
        Invoke the chain.
        """
        return self._get_chain.invoke(message)


    def ainvoke(self, message: str) -> str:
        """
        Ainvoke the chain.
        """
        return self._get_chain.ainvoke(message)
    
    def get(self) -> Runnable:
        """
        Return the configured chain.
        """
        return self._get_chain
