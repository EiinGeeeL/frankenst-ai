import logging
from typing import Any
from typing import Iterable, Tuple, Union
from langgraph.prebuilt import ToolNode
from frankstate.entity.node import BaseNode, SimpleNode, CommandNode
from frankstate.entity.statehandler import StateCommander, StateEnhancer

class NodeManager:
    """Store graph node definitions and expose them in `StateGraph` format.

    The manager accepts project nodes (`SimpleNode`, `CommandNode`) and native
    LangGraph `ToolNode` instances. During configuration it resolves each node
    to the callable consumed by `StateGraph.add_node()`.

    Node names are treated as a Frankenst-AI contract invariant: registration keeps
    insertion order and rejects duplicate names before delegating to LangGraph.
    """

    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])
    
    def __init__(self):
        self.nodes: dict[str, Union[SimpleNode, CommandNode, ToolNode]] = {}
        self.logger.info("NodeManager initialized")
    
    def _normalize_nodes(self, nodes: Union[SimpleNode, CommandNode, ToolNode] | Iterable[Union[SimpleNode, CommandNode, ToolNode]]) -> list[Union[SimpleNode, CommandNode, ToolNode]]:
        """Return nodes as a list while supporting single-node inputs."""
        if isinstance(nodes, (SimpleNode, CommandNode, ToolNode)):
            return [nodes]

        return list(nodes)

    def _get_node_value(self, node: Union[SimpleNode, CommandNode, ToolNode]) -> Any:
        """Resolve a node wrapper to the callable or ToolNode added to the graph."""
        if isinstance(node, ToolNode):
            return node
        elif isinstance(node, SimpleNode):
            return node.enhancer.enhance
        elif isinstance(node, CommandNode):
            return node.commander.command
        else:
            raise TypeError(f"Unexpected node type: {type(node)}")

    def _get_node_tags(self, node: Union[SimpleNode, CommandNode, ToolNode]) -> list[str] | None:
        """Return node tags for wrappers or native ToolNode instances.

        Wrapper nodes expose `tags` directly. Native `ToolNode` already uses the
        same attribute name in LangGraph.
        """
        return node.tags if isinstance(node, BaseNode) else getattr(node, "tags", None)

    def add_nodes(self, nodes: Union[SimpleNode, CommandNode, ToolNode] | Iterable[Union[SimpleNode, CommandNode, ToolNode]]) -> None:
        """
        Add one or more supported node instances to the internal registry.

        Accepted inputs are `SimpleNode`, `CommandNode`, `ToolNode` or a list
        containing any mix of those types.
        """
        for node in self._normalize_nodes(nodes):
            if isinstance(node, (SimpleNode, CommandNode, ToolNode)):
                if node.name in self.nodes:
                    raise ValueError(f"Node name '{node.name}' is already registered")
                self.nodes[node.name] = node
            else:
                raise TypeError(f"Unexpected node type: {type(node)}")

    def get_nodes(self) -> Tuple[Union[SimpleNode, CommandNode, ToolNode], ...]:
        """
        Retrieve all registered nodes preserving insertion order.
        """
        return tuple(self.nodes.values())

    def configs_nodes(self) -> Tuple[Tuple[str, Any, list[str] | None, Union[Tuple[str, ...], None]], ...]:
        """
        Retrieve deterministic `(name, callable, tags, destinations)` tuples.

        `tags` are the Frankenst-AI annotation surface. `WorkflowBuilder`
        forwards them to `StateGraph.add_node(metadata=...)` for wrapper nodes.
        `destinations` is a tuple of reachable node names for `CommandNode`
        instances (consumed by `StateGraph.add_node(destinations=...)` for graph
        rendering). It is `None` for all other node types.

        The returned callable may be synchronous or asynchronous. LangGraph
        accepts both forms for node execution.
        """
        return tuple(
            (
                name,
                self._get_node_value(node),
                self._get_node_tags(node),
                node.destinations if isinstance(node, CommandNode) else None,
            )
            for name, node in self.nodes.items()
        )

    def remove_node(self, node: Union[SimpleNode, CommandNode, ToolNode]) -> None:
        """
        Remove a specific node from the registry by name.
        """
        if node.name in self.nodes:
            self.nodes.pop(node.name)
        else:
            raise ValueError(f"Node name '{node.name}' is not registered")
