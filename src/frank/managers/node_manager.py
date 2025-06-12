import logging
from typing import Set, List, Tuple, Union
from langgraph.prebuilt import ToolNode
from frank.entity.node import SimpleNode, CommandNode
from frank.entity.statehandler import StateEnhancer, StateCommander

class NodeManager:
    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])
    
    def __init__(self):
        self.nodes : Set[Union[SimpleNode, ToolNode]] = set()
        self.logger.info("NodeManager initialized")
    
    def _get_node_value(self, node: Union[ToolNode, SimpleNode, CommandNode]) -> Union[StateEnhancer.enhance, StateCommander.command, ToolNode]:
        if isinstance(node, ToolNode):
            return node
        elif isinstance(node, SimpleNode):
            return node.enhancer.enhance
        elif isinstance(node, CommandNode):
            return node.commander.command
        else:
            raise TypeError(f"Unexpected node type: {type(node)}")

    def add_nodes(self, nodes: Union[SimpleNode, ToolNode, List[Union[SimpleNode, ToolNode]]]) -> None:
        """
        Add one or more SimpleNode or ToolNode instances to the set.
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
        Retrieve a set containing all added nodes.
        """
        return self.nodes

    def configs_nodes(self) -> Tuple[Tuple[str, Union[StateEnhancer.enhance, StateCommander.command, ToolNode]]]:
        """
        Retrieve a node configuration for StateGraph.
        """
        return (
            (node.name, self._get_node_value(node))
            for node in self.nodes
        )
    def remove_node(self, node: Union[SimpleNode, CommandNode, ToolNode]) -> None:
        """
        Remove a specific node from the set.
        """
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            raise ValueError("Node not found in the set")
