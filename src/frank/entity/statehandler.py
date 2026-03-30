from abc import ABC, abstractmethod
from typing import Literal, Any, Optional, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from langgraph.types import Command
from frank.entity.runnable_builder import RunnableBuilder

class StateEvaluator(ABC):
    """Base contract for conditional routing in a LangGraph StateGraph.

    Implementations receive the current graph state and must return a routing key
    that exists in the corresponding `ConditionalEdge.map_dict`.

    Typical usage:
    - Read a subset of the current state.
    - Evaluate a condition.
    - Return a short routing key such as `"tools"`, `"rewrite"` or `"end"`.

    This contract mirrors the callable passed to `StateGraph.add_conditional_edges()`.
    """

    def __init__(
        self,
        runnable_builder: Optional[RunnableBuilder] = None,
        **kwargs: Any,

        ):
        self.runnable = runnable_builder.get() if runnable_builder else None

        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    async def evaluate(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> str:
        """Return the routing key used by a conditional edge path map.

        The returned value must match one of the keys declared in the
        `ConditionalEdge.map_dict` for the edge that uses this evaluator.
        """
        pass


class StateEnhancer(ABC):
    """Base contract for node callables that return partial state updates.

    This wrapper keeps the project API stable while matching the official
    LangGraph pattern where a node receives the current state and returns a
    partial update that LangGraph merges into the state.

    In the example graphs, enhancers commonly append new values to `messages`
    and may also add or update scalar keys required by the graph schema, such as
    `question`, `generation` or `iterations`.
    """

    def __init__(
            self,
            runnable_builder: Optional[RunnableBuilder] = None,
            **kwargs: Any,
        ):
        
        self.runnable = runnable_builder.get() if runnable_builder else None
         
        for key, value in kwargs.items():
            setattr(self, key, value)

        
        
    @abstractmethod
    async def enhance(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> dict[str, list]:
        """Return a partial state update produced by runnable or custom enhance logic.

        The returned mapping is merged by LangGraph into the current state. The
        exact keys must be compatible with the graph state schema used when the
        workflow is compiled.
        """
        pass

class StateCommander:
    """Base contract for nodes that route with LangGraph Command.

    Use this abstraction only when routing and state updates must happen in the
    same node callable, such as human-in-the-loop flows or supervisor patterns.

    Unlike `StateEvaluator`, a commander does not rely on a separate
    `ConditionalEdge`. It returns an official `Command` object with a `goto`
    destination and optional state updates.
    """
    # Example config_node.yml read structure used by commander implementations.
    # This is illustrative documentation, not runtime configuration.
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
        """Modify the StateGraph and also route with Command[Literal] to nodes. 
        No need edges or conditional edges, the command method contain the logic routing.
        This is usefull for Human in the Loop and Multi-Agent or Agent Supervisors apps.
        """

        # Implementation would go here
        pass

        return Command(goto=StateCommander.config_nodes['current_node']['route']['tools'])