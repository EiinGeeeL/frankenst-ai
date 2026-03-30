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

class WorkflowBuilder:
    """Assemble a LangGraph `StateGraph` from a layout dataclass.

    The builder expects a layout compatible with `GraphLayout`, a state schema
    compatible with LangGraph and optional input, output and checkpointing
    primitives. The public flow is:

    1. Instantiate the builder with a layout and a state schema.
    2. Call `compile()`.
    3. Invoke the returned compiled graph from notebooks, services or apps.
    """

    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])
    
    def __init__(self, config: Type[Any], state_schema: Type[Any], checkpointer: Optional[BaseCheckpointSaver] = None, input_schema: Optional[Type[Any]] = None, output_schema: Optional[Type[Any]] = None):
        """Create a workflow builder for a graph layout.

        Args:
            config: Dataclass layout containing nodes, edges and optional helper builders.
            state_schema: LangGraph state schema used by `StateGraph`.
            checkpointer: Optional LangGraph checkpoint saver.
            input_schema: Optional input schema forwarded to `StateGraph`.
            output_schema: Optional output schema forwarded to `StateGraph`.
        """
        self.workflow: StateGraph = StateGraph(state_schema=state_schema, input_schema=input_schema, output_schema=output_schema)
        self.memory: Optional[BaseCheckpointSaver] = checkpointer
        self.config: GraphLayout = GraphLayout(config)
        self.edge_manager: EdgeManager = EdgeManager()
        self.node_manager: NodeManager = NodeManager()
        
        self.logger.info(f"WorkFlowBuilder initialized for GraphLayout {config.__name__}")

    def compile(self) -> CompiledStateGraph:
        """Configure nodes and edges declared in the layout, then compile the graph."""
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
        """Assemble the workflow from the nodes and edges discovered in the layout."""
        self._configure_nodes()
        [self.workflow.add_node(*config) for config in self.node_manager.configs_nodes()]

        self._configure_edges()
        [self.workflow.add_edge(*config) for config in self.edge_manager.configs_edges()]
        [self.workflow.add_conditional_edges(*config) for config in self.edge_manager.configs_conditional_edges()]  
    
    def _configure_nodes(self) -> None:
        """Load node definitions from the layout into the node manager."""
        self.node_manager.add_nodes(nodes=self.config.get_nodes())

    def _configure_edges(self) -> None:
        """Load edge definitions from the layout into the edge manager."""        
        self.edge_manager.add_edges(edges=self.config.get_edges())