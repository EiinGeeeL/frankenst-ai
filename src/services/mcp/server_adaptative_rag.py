from mcp.server.fastmcp import FastMCP


mcp = FastMCP("AdaptativeRAG")

@mcp.tool()
async def adaptive_rag_tool(input: str) -> str:
    """Tool to use RAG about Pokémon series questions. The input is a question."""
    from frankstate import WorkflowBuilder
    from core_examples.config.layouts.local_vectorstore_adaptive_rag_config_graph import LocalVectorStoreAdaptiveRAGConfigGraph
    from core_examples.models.stategraph.ragstategraph import RAGState
    from core_examples.utils.common import read_yaml
    from core_examples.utils.logger import setup_logging
    from core_examples.constants import CONFIG_FILE_PATH

    config = read_yaml(CONFIG_FILE_PATH)
    setup_logging(config)

    workflow_builder = WorkflowBuilder(
        config=LocalVectorStoreAdaptiveRAGConfigGraph,
        state_schema=RAGState,
    )
    ADAPTATIVE_RAG_GRAPH = workflow_builder.compile()

    message_input = {"messages": [{"role": "human", "content": input}]}
    response = await ADAPTATIVE_RAG_GRAPH.ainvoke(message_input)
    return response['messages'][-1].content

if __name__ == "__main__":
    mcp.run(transport="streamable-http")