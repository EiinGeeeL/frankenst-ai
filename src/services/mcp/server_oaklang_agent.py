from mcp.server.fastmcp import FastMCP


mcp = FastMCP("OakLangAgent")

@mcp.tool()
async def handoff_oaklang_agent_tool(input: str) -> str:
    """Tool to use OakLangAgent about any Pokemon question. The input is a question."""
    from frankstate import WorkflowBuilder
    from core_examples.config.layouts.oak_human_loop_config_graph import OakHumanLoopConfigGraph
    from core_examples.constants import CONFIG_FILE_PATH
    from core_examples.models.stategraph.stategraph import SharedState
    from core_examples.utils.common import read_yaml
    from core_examples.utils.logger import setup_logging

    config = read_yaml(CONFIG_FILE_PATH)
    setup_logging(config)

    workflow_builder = WorkflowBuilder(
        config=OakHumanLoopConfigGraph, 
        state_schema=SharedState,
    )
    OAKLANG_AGENT_GRAPH = workflow_builder.compile()

    message_input = {"messages": [{"role": "human", "content": input}]}
    response = await OAKLANG_AGENT_GRAPH.ainvoke(message_input)
    return response['messages'][-1].content

if __name__ == "__main__":
    mcp.run(transport="stdio")
