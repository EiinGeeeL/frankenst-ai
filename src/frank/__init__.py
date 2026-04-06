"""Public root API for the reusable `frank` package.

Only `WorkflowBuilder` is re-exported from the package root.

All other reusable building blocks must be imported from their concrete
submodules so that `frank` does not become an absolute import bucket. Examples:

- `from frank.entity.graph_layout import GraphLayout`
- `from frank.entity.node import SimpleNode, CommandNode`
- `from frank.entity.edge import SimpleEdge, ConditionalEdge`
- `from frank.entity.statehandler import StateEnhancer, StateEvaluator, StateCommander`
- `from frank.entity.runnable_builder import RunnableBuilder`
- `from frank.managers.node_manager import NodeManager`
- `from frank.managers.edge_manager import EdgeManager`
"""

from frank.workflow_builder import WorkflowBuilder

__all__ = ["WorkflowBuilder"]
