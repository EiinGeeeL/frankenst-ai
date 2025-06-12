from frank.workflow_builder import WorkflowBuilder
from frank.config.layouts.adaptative_rag_config_graph import AdaptativeRAGConfigGraph
from frank.entity.models.ragstategraph import RAGState
from frank.utils.common import read_yaml
from frank.utils.logger import setup_logging
from frank.constants import *

## Read the config.yaml
config = read_yaml(CONFIG_FILE_PATH)

## Setup logging Configuration
setup_logging(config)

## Workflow Configuration for the main graph
workflow_builder = WorkflowBuilder(
    config=AdaptativeRAGConfigGraph, 
    state_schema=RAGState,
)
ADAPTATIVE_RAG_GRAPH = workflow_builder.compile() # compile the graph

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("AdaptativeRAG")

@mcp.tool()
async def adaptive_rag_tool(input: str) -> str:
    """Tool to use RAG about Pokémon series questions. The input is a question."""
    message_input = {"messages": [{"role": "human", "content": input}]}
    response = await ADAPTATIVE_RAG_GRAPH.ainvoke(message_input)
    return response['messages'][-1].content

if __name__ == "__main__":
    mcp.run(transport="streamable-http")