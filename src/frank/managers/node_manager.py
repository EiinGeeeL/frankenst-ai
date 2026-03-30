import logging
from typing import Set, List, Tuple, Union
from langgraph.prebuilt import ToolNode
from frank.entity.node import SimpleNode, CommandNode
from frank.entity.statehandler import StateEnhancer, StateCommander

class NodeManager:
    """Store graph node definitions and expose them in `StateGraph` format.

    The manager accepts project nodes (`SimpleNode`, `CommandNode`) and native
    LangGraph `ToolNode` instances. During configuration it resolves each node
    to the callable consumed by `StateGraph.add_node()`.
    """

    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])
    
    def __init__(self):
        self.nodes : Set[Union[SimpleNode, CommandNode, ToolNode]] = set()
        self.logger.info("NodeManager initialized")
    
    def _get_node_value(self, node: Union[ToolNode, SimpleNode, CommandNode]) -> Union[StateEnhancer.enhance, StateCommander.command, ToolNode]:
        """Resolve a node wrapper to the callable or ToolNode added to the graph."""
        if isinstance(node, ToolNode):
            return node
        elif isinstance(node, SimpleNode):
            return node.enhancer.enhance
        elif isinstance(node, CommandNode):
            return node.commander.command
        else:
            raise TypeError(f"Unexpected node type: {type(node)}")

    def add_nodes(self, nodes: List[Union[SimpleNode, CommandNode, ToolNode]]) -> None:
        """
        Add one or more supported node instances to the internal registry.

        Accepted inputs are `SimpleNode`, `CommandNode`, `ToolNode` or a list
        containing any mix of those types.
        """
        if not isinstance(nodes, list):
            nodes = [nodes]

        for node in nodes:
            if isinstance(node, (SimpleNode, CommandNode, ToolNode)):
                self.nodes.add(node)
            else:
                raise TypeError(f"Unexpected node type: {type(node)}")

    def get_nodes(self) -> Set[Union[SimpleNode, CommandNode, ToolNode]]:
        """
        Retrieve the set containing all registered nodes.
        """
        return self.nodes

    def configs_nodes(self) -> Tuple[Tuple[str, Union[StateEnhancer.enhance, StateCommander.command, ToolNode]]]:
        """
        Retrieve `(name, callable)` tuples compatible with `StateGraph.add_node()`.
        """
        return (
            (node.name, self._get_node_value(node))
            for node in self.nodes
        )
    def remove_node(self, node: Union[SimpleNode, CommandNode, ToolNode]) -> None:
        """
        Remove a specific node from the registry.
        """
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            raise ValueError("Node not found in the set")
