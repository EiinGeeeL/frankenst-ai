from langgraph.checkpoint.memory import MemorySaver
from frank.workflow_builder import WorkflowBuilder
from frank.config.config_graph import ConfigGraph
from frank.entity.models.stategraph import SharedState
from frank.utils.common import read_yaml
from frank.utils.logger import setup_logging
from frank.constants import *

## Read the config.yaml
config = read_yaml(CONFIG_FILE_PATH)

## Setup logging Configuration
setup_logging(config)

## Workflow Configuration for the main graph
workflow_builder = WorkflowBuilder(
    config=ConfigGraph, 
    state_schema=SharedState, 
    checkpointer=MemorySaver(),
)
main_graph = workflow_builder.compile() # compile the graph
workflow_builder.display_graph(save=True, filepath="artifacts/graph.png") # update the graph artifact