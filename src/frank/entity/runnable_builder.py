from abc import ABC, abstractmethod
from typing import List, Any
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from services.llm import LLMServices


class RunnableBuilder(ABC):
    def __init__(
        self,
        model: LLMServices,
        vectordb: Any, # TODO define class 
        tools: List[BaseTool]
    ):
        self.model = model
        self.vectordb = vectordb
        self.tools = tools

        # Start the chain
        self._chain: Runnable = None

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
        
    def get(self) -> Runnable:
        """
        Return the configured chain.
        """
        return self._get_chain
