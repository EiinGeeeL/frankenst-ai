from abc import ABC, abstractmethod
from typing import Literal, Any
from langgraph.graph import StateGraph
from langgraph.types import Command
from frank.entity.runnable_builder import RunnableBuilder
from frank.utils.common import read_yaml
from frank.constants import *


class StateEvaluator(ABC):
    @abstractmethod
    async def evaluate(self, state: StateGraph) -> str: 
        """
        Returns a str to generate a conditional path_map to rotute the StateGraph 
       
        """
        pass


class StateEnhancer(ABC): 
    def __init__(
            self,
            runnable_builder: RunnableBuilder
        ):
        self.runnable = runnable_builder.get()
        
    @abstractmethod
    async def enhance(self, state: StateGraph) -> dict[Literal["message"]: list]:
        """
        Returns StateGraph with modifications made by a Runnable.
        """
        pass

class StateCommander:
    # Nodes config to route the command
    config_nodes: dict = read_yaml(CONFIG_NODES_FILE_PATH)

    @staticmethod
    def command(state: StateGraph(state_schema=Any)) -> Command[Literal[...]]: # type: ignore
        """
        Modify the StateGraph and also route with Command[Literal] to nodes. 
        No need edges or conditional edges, the command method contain the logic routing.
        This is usefull for Human in the Loop and Multi-Agent or Agent Supervisors apps.
        """

    # Implementation would go here
        pass