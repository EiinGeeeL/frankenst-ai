from mcp.server.fastmcp import FastMCP

mcp = FastMCP("OakLangAgent")

@mcp.tool()
async def oaklang_agent_tool(input: str) -> str:
    from frank.workflow_builder import WorkflowBuilder
    from frank.config.layouts.oak_human_loop_config_graph import OakHumanLoopConfigGraph
    from frank.models.stategraph.stategraph import SharedState
    from frank.utils.common import read_yaml
    from frank.utils.logger import setup_logging
    from frank.constants import CONFIG_FILE_PATH

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
