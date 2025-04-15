from typing import Union, Literal, Dict
from frank.entity.statehandler import StateEvaluator

# Common base for all Edge types
class BaseEdge():
    def __init__(self, node_source: Union[str, Literal["START", "END"]]):
        self.node_source = node_source

# SimpleEdge: follows a static path
class SimpleEdge(BaseEdge):
    def __init__(
        self, 
        node_source: Union[str, Literal["START", "END"]],
        node_path: Union[str, Literal["START", "END"]]
    ):
        super().__init__(node_source)
        self.node_path = node_path


# ConditionalEdge: chooses path dynamically
class ConditionalEdge(BaseEdge):
    def __init__(
        self,
        node_source: Union[str, Literal["START", "END"]],
        map_dict: Dict[str, Union[str, Literal["START", "END"]]],
        evaluator: StateEvaluator
    ):
        super().__init__(node_source)
        self.map_dict = map_dict
        self.evaluator = evaluator