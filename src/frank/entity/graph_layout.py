import logging
from dataclasses import is_dataclass
from typing import Any, Type

from langgraph.prebuilt import ToolNode

from frank.entity.edge import BaseEdge
from frank.entity.node import BaseNode
from frank.entity.runnable_builder import RunnableBuilder

class GraphLayout:
    """Introspect a dataclass layout and expose its graph-related attributes.

    Layouts in this project are class-like dataclasses whose attributes declare
    nodes, edges and optional runnable builders. `WorkflowBuilder` relies on
    this introspection step instead of manually wiring each component.
    """

    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])

    def __init__(self, config: Type[Any]):
        """Initialize the Graph Layout with a dataclass TYPE
        containing configuration constants like edges and nodes.

        Args:
            config (Type[Any]): A dataclass type that defines nodes and edges.

        Notes:
            The dataclass is expected to expose `BaseNode`, `ToolNode`,
            `BaseEdge` and optional `RunnableBuilder` instances as attributes.
        """
        
        if not is_dataclass(config):
            raise TypeError("Expected a dataclass type for the GraphLayout configuration that defines nodes and edges")
        else:
            self.config = config

        self.logger.info('GraphLayout initialized')
        
    def get_nodes(self):
        """Return nodes declared as class attributes in the layout dataclass.

        Only instances compatible with `BaseNode` or `ToolNode` are returned.
        Any other helper attributes remain ignored by the graph assembly logic.
        """
        return [
            attr_value 
            for attr_value in self.config.__dict__.values() 
            if isinstance(attr_value, (BaseNode, ToolNode))
        ]

    def get_edges(self):
        """Return edges declared as class attributes in the layout dataclass.

        Only instances compatible with `BaseEdge` are returned.
        """
        return [
            attr_value 
            for attr_value in self.config.__dict__.values() 
            if isinstance(attr_value, (BaseEdge))
        ]

    def get_runnable_builders(self):
        """Return runnable builders declared in the layout dataclass.

        This helper is mainly useful for inspection and debugging; the workflow
        builder compiles graphs from nodes and edges.
        """
        return [
            attr_value 
            for attr_value in self.config.__dict__.values() 
            if isinstance(attr_value, RunnableBuilder)
        ]
