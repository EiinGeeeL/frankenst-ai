import logging
import inspect
from typing import Any, Optional, Type
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from frankstate.entity.graph_layout import GraphLayout
from frankstate.managers.edge_manager import EdgeManager
from frankstate.managers.node_manager import NodeManager
from langgraph.checkpoint.base import BaseCheckpointSaver

class WorkflowBuilder:
    """Assemble a LangGraph `StateGraph` from a `GraphLayout` subclass.

    The builder accepts a layout class that inherits from `GraphLayout`, plus
    a state schema compatible with LangGraph and optional input, output and
    checkpointing primitives. The public flow is:

    1. Instantiate the builder with a layout and a state schema.
    2. Call `compile()`.
    3. Invoke the returned compiled graph from notebooks, services or apps.
    """

    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])
    
    def __init__(self, config: Type[Any], state_schema: Type[Any], checkpointer: Optional[BaseCheckpointSaver] = None, input_schema: Optional[Type[Any]] = None, output_schema: Optional[Type[Any]] = None):
        """Create a workflow builder for a graph layout.

        Args:
            config: Layout class inheriting from `GraphLayout`.
            state_schema: LangGraph state schema used by `StateGraph`.
            checkpointer: Optional LangGraph checkpoint saver.
            input_schema: Optional input schema forwarded to `StateGraph`.
            output_schema: Optional output schema forwarded to `StateGraph`.
        """
        self.workflow: StateGraph = StateGraph(state_schema=state_schema, input_schema=input_schema, output_schema=output_schema)
        self.memory: Optional[BaseCheckpointSaver] = checkpointer

        if not inspect.isclass(config) or not issubclass(config, GraphLayout):
            raise TypeError(
                "WorkflowBuilder expects `config` to be a GraphLayout subclass"
            )

        self.config: GraphLayout = config()
        self.edge_manager: EdgeManager = EdgeManager()
        self.node_manager: NodeManager = NodeManager()
        self._workflow_configured: bool = False
        
        self.logger.info(f"WorkFlowBuilder initialized for GraphLayout {config.__name__}")

    def compile(self) -> CompiledStateGraph:
        """Configure nodes and edges declared in the layout, then compile the graph."""
        self._ensure_workflow_configured()
        return self.workflow.compile(checkpointer=self.memory)
    
    def display_graph(self, save: bool = False, filepath: str = "graph.png") -> None:
        """
        Display the compiled graph or save as a PNG image.
        """
        try:
            from IPython.display import Image, display
            from langchain_core.runnables.graph import MermaidDrawMethod
        except ImportError as exc:
            raise ImportError(
                "display_graph() requires notebook dependencies to render Mermaid diagrams."
            ) from exc

        temp_graph = self.compile()
        img_data = temp_graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API,)

        if save:
            with open(filepath, "wb") as f:
                f.write(img_data)
            return

        display(Image(img_data))

    def _ensure_workflow_configured(self) -> None:
        """Configure the workflow once before any compile or visualization step."""
        if not self._workflow_configured:
            self._configure_workflow()
        
    def _configure_workflow(self) -> None:
        """Assemble the workflow from the nodes and edges discovered in the layout."""
        self._configure_nodes()
        for node_args, node_kwargs in self.node_manager.configs_nodes():
            self.workflow.add_node(*node_args, **node_kwargs)

        self._configure_edges()
        for config in self.edge_manager.configs_edges():
            self.workflow.add_edge(*config)
        for node_source, router, path_map in self.edge_manager.configs_conditional_edges():
            self.workflow.add_conditional_edges(
                node_source,
                router,
                path_map=path_map,
            )

        self._workflow_configured = True
    
    def _configure_nodes(self) -> None:
        """Load node definitions from the layout into the node manager."""
        self.node_manager.add_nodes(nodes=self.config.get_nodes())

    def _configure_edges(self) -> None:
        """Load edge definitions from the layout into the edge manager."""        
        self.edge_manager.add_edges(edges=self.config.get_edges())