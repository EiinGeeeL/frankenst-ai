import logging
from typing import Type, Any, Optional
from IPython.display import Image, display
from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from frank.entity.graph_layout import GraphLayout
from frank.managers.edge_manager import EdgeManager
from frank.managers.node_manager import NodeManager
from langgraph.checkpoint.base import BaseCheckpointSaver

## Graph Configuration
class WorkflowBuilder:
    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])
    
    def __init__(self, config: Type[Any], state_schema: Type[Any], checkpointer: Optional[BaseCheckpointSaver] = None, input: Optional[Type[Any]] = None, output: Optional[Type[Any]] = None):
        self.workflow: StateGraph = StateGraph(state_schema=state_schema, input=input, output=output)
        self.memory: Optional[BaseCheckpointSaver] = checkpointer
        self.config: GraphLayout = GraphLayout(config)
        self.edge_manager: EdgeManager = EdgeManager()
        self.node_manager: NodeManager = NodeManager()
        
        self.logger.info(f"WorkFlowBuilder initialized for GraphLayout {config.__name__}")

    def compile(self) -> CompiledStateGraph:
        self._configure_workflow()
        return self.workflow.compile(checkpointer=self.memory)
    
    def display_graph(self, save: bool = False, filepath: str = "graph.png") -> Image:
        """
        Display the compiled graph or save as a PNG image.
        """
        tmp_graph = self.workflow.compile()
        img_data = tmp_graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API,)

        if save:
            with open(filepath, "wb") as f:
                f.write(img_data)
        else:
            return display(Image(img_data))
        
    def _configure_workflow(self) -> None:
        """
        Ensemble the graph workflow.
        """
        # Configure the nodes
        self._configure_nodes()
        [self.workflow.add_node(*config) for config in self.node_manager.configs_nodes()]

        # Configure the edges
        self._configure_edges()
        [self.workflow.add_edge(*config) for config in self.edge_manager.configs_edges()]
        [self.workflow.add_conditional_edges(*config) for config in self.edge_manager.configs_conditional_edges()]  
    
    def _configure_nodes(self) -> None:
        """
        Fill the nodes in manager.
        """
        self.node_manager.add_nodes(nodes=self.config.get_nodes())

    def _configure_edges(self) -> None:
        """
        Fill the edges in manager.
        """        
        self.edge_manager.add_edges(edges=self.config.get_edges())