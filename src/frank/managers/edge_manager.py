import logging
from typing import Union, Set, List, Type, Tuple, Callable, Dict
from frank.entity.edge import SimpleEdge, ConditionalEdge
from frank.entity.statehandler import StateEvaluator

class EdgeManager:
    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])
    edges: set[Union[SimpleEdge, ConditionalEdge]] = set()  
    
    def __init__(self):
        self.logger.info("EdgeManager initialized")

    def add_edges(self, edges: List[Union[SimpleEdge, ConditionalEdge]]) -> None:
        """
        Add one or more edges to the appropriate set based on their type.

        """

        for edge in edges:
            if isinstance(edge, (SimpleEdge, ConditionalEdge)):
                self.edges.add(edge)
            else:
                raise TypeError(f"Each edge must be a SimpleEdge or ConditionalEdge, got {type(edge)}")

    def get_edges(self, filter_type: Union[Type[SimpleEdge], Type[ConditionalEdge], None] = None) -> Union[Set[Union[SimpleEdge, ConditionalEdge]], Set[SimpleEdge], Set[ConditionalEdge]]:
        """
        Retrieve your edges, optionally filtered by type.
        """
        if filter_type is None:
            return self.edges
        elif issubclass(filter_type, (SimpleEdge, ConditionalEdge)):
            return {edge for edge in self.edges if type(edge) == filter_type}
        else:
            raise TypeError(f"Each edge must be a SimpleEdge or ConditionalEdge, expected {type(filter_type)}")

    def configs_edges(self) -> Tuple[Tuple[str, str]]:
        """
        Returns a tuple with node source and node path.
        """
        return ((edge.node_source, edge.node_path) 
                for edge in self.edges if type(edge) == SimpleEdge)
    
    def configs_conditional_edges(self) -> Tuple[Tuple[str, Callable[..., StateEvaluator.evaluate], Dict[str, str]]]:
        """
        Returns a configs containing:
        - A string representing the source node
        - A function (any callable) to apply as conditional edge
        - A dictionary with conditions between the nodes
        """
        return ((edge.node_source, edge.evaluator.evaluate, edge.map_dict) 
                for edge in self.edges if type(edge) != SimpleEdge)
