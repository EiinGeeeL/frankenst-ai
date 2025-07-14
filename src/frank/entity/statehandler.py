from abc import ABC, abstractmethod
from typing import Literal, Any, Optional, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from langgraph.types import Command
from frank.entity.runnable_builder import RunnableBuilder

class StateEvaluator(ABC):
    def __init__(
        self,
        runnable_builder: Optional[RunnableBuilder] = None
    ):
        self.runnable = runnable_builder.get() if runnable_builder else None

    @abstractmethod
    async def evaluate(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> str:
        """
        Returns a str to generate a conditional path_map to route the StateGraph.
        """
        pass


class StateEnhancer(ABC): 
    def __init__(
            self,
            runnable_builder: Optional[RunnableBuilder] = None
        ):
        self.runnable = runnable_builder.get() if runnable_builder else None
        
    @abstractmethod
    async def enhance(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> dict[Literal[str]: list]:
        """
        Returns a StateGraph with modifications applied via Runnable 
        or through custom enhance logic.        
        """
        pass

class StateCommander:
    # Example config_node.yml read structure to route the command to node names
    config_nodes: dict[str, dict[str, dict[str, str]]] = {
        "current_node": {
            "name" : "current_node_name",
            "type" : "commander",
            "route": {
                "tools": "some_tool_node_name",
                "enhancer_b": "other_node_name",
                "enhancer_c": "another_node_name",
            }
        }
    }

    @staticmethod
    def command(state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> Command[Literal[tuple(config_nodes['current_node']['route'].values())]]: # type: ignore
        """
        Modify the StateGraph and also route with Command[Literal] to nodes. 
        No need edges or conditional edges, the command method contain the logic routing.
        This is usefull for Human in the Loop and Multi-Agent or Agent Supervisors apps.
        """

    # Implementation would go here
        pass

        return Command(goto=StateCommander.config_nodes['current_node']['route']['tools'])