import logging
from langgraph.prebuilt import ToolNode
from dataclasses import is_dataclass
from typing import Type, Any
from frank.entity.edge import BaseEdge
from frank.entity.node import BaseNode
from frank.entity.runnable_builder import RunnableBuilder

class GraphLayout:
    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])

    def __init__(self, config: Type[Any]):
        """
        Initialize the Graph Layout with a dataclass TYPE
        containing configuration constants like edges and nodes.

        Args:
            config (Type[Any]): A dataclass type that defines nodes and edges
        """
        
        if not is_dataclass(config):
            raise TypeError("Expected a dataclass type for the GraphLayout configuration that defines nodes and edges")
        else:
            self.config = config

        self.logger.info('GraphLayout initialized')
        
    def get_nodes(self):
        """
        Returns a list of all nodes defined in the configuration dataclass.
        """
        return [
            attr_value 
            for attr_value in self.config.__dict__.values() 
            if isinstance(attr_value, (BaseNode, ToolNode))
        ]

    def get_edges(self):
        """
        Returns a list of all edges defined in the configuration dataclass.
        """
        return [
            attr_value 
            for attr_value in self.config.__dict__.values() 
            if isinstance(attr_value, (BaseEdge))
        ]

    def get_runnable_builders(self):
        """
        Returns a list of all runnable builders defined in the configuration dataclass.
        """
        return [
            attr_value 
            for attr_value in self.config.__dict__.values() 
            if isinstance(attr_value, RunnableBuilder)
        ]
