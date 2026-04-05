import asyncio

import pytest
from langchain_core.messages import HumanMessage

from frank.workflow_builder import WorkflowBuilder
from tests.support.frank_doubles import (
    CommandAsyncLayout,
    ConditionalAsyncEvaluatorLayout,
    ConditionalAsyncLayout,
    FrankTestState,
    LinearAsyncLayout,
    LinearSyncLayout,
    ToolLoopLayout,
)


@pytest.mark.unit
def test_workflow_builder_rejects_non_graphlayout_config() -> None:
    with pytest.raises(TypeError, match="GraphLayout subclass"):
        WorkflowBuilder(config=object, state_schema=FrankTestState)


@pytest.mark.unit
def test_workflow_builder_compiles_linear_layout_once_and_runs_async_enhancer() -> None:
    builder = WorkflowBuilder(config=LinearAsyncLayout, state_schema=FrankTestState)

    first_compiled = builder.compile()
    second_compiled = builder.compile()
    result = asyncio.run(first_compiled.ainvoke({"messages": [HumanMessage(content="hi")]}))

    assert first_compiled is not None
    assert second_compiled is not None
    assert builder._workflow_configured is True
    assert builder.config.runtime_calls == 1
    assert builder.config.layout_calls == 1
    assert result["messages"][-1].content == "linear-response"
    assert first_compiled.get_graph().nodes["linear_node"].metadata == {"tags": ["linear"]}


@pytest.mark.unit
def test_workflow_builder_compiles_linear_layout_and_runs_sync_enhancer() -> None:
    builder = WorkflowBuilder(config=LinearSyncLayout, state_schema=FrankTestState)

    compiled = builder.compile()
    result = compiled.invoke({"messages": [HumanMessage(content="hi")]})

    assert result["messages"][-1].content == "linear-sync-response"
    assert compiled.get_graph().nodes["linear_sync_node"].metadata == {"tags": ["linear-sync"]}


@pytest.mark.unit
@pytest.mark.parametrize(
    ("route", "expected"),
    [("accept", "accepted"), ("reject", "rejected")],
)
def test_workflow_builder_routes_conditional_edges_through_langgraph(route: str, expected: str) -> None:
    builder = WorkflowBuilder(config=ConditionalAsyncLayout, state_schema=FrankTestState)
    compiled = builder.compile()

    result = asyncio.run(
        compiled.ainvoke(
            {
                "messages": [HumanMessage(content="hi")],
                "route": route,
            }
        )
    )

    assert result["messages"][-1].content == expected
    assert set(compiled.get_graph().nodes) >= {
        "__start__",
        "router_node",
        "accept_node",
        "reject_node",
        "__end__",
    }


@pytest.mark.unit
@pytest.mark.parametrize(
    ("route", "expected"),
    [("accept", "accepted"), ("reject", "rejected")],
)
def test_workflow_builder_routes_async_evaluators_through_langgraph(route: str, expected: str) -> None:
    builder = WorkflowBuilder(config=ConditionalAsyncEvaluatorLayout, state_schema=FrankTestState)
    compiled = builder.compile()

    result = asyncio.run(
        compiled.ainvoke(
            {
                "messages": [HumanMessage(content="hi")],
                "route": route,
            }
        )
    )

    assert result["messages"][-1].content == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    ("decision", "expected_message"),
    [("accept", "accepted"), ("reject", "rejected")],
)
def test_workflow_builder_routes_command_nodes_and_applies_updates(decision: str, expected_message: str) -> None:
    builder = WorkflowBuilder(config=CommandAsyncLayout, state_schema=FrankTestState)
    compiled = builder.compile()

    result = asyncio.run(
        compiled.ainvoke(
            {
                "messages": [HumanMessage(content="hi")],
                "decision": decision,
            }
        )
    )

    assert result["decision"] == decision
    assert result["messages"][-2].content == f"command:{decision}"
    assert result["messages"][-1].content == expected_message
    assert builder.node_manager.nodes["command_node"].destinations == ("accept_node", "reject_node")


@pytest.mark.unit
def test_workflow_builder_integrates_toolnode_with_frank_nodes() -> None:
    builder = WorkflowBuilder(config=ToolLoopLayout, state_schema=FrankTestState)
    compiled = builder.compile()

    result = asyncio.run(
        compiled.ainvoke(
            {
                "messages": [HumanMessage(content="use a tool")],
                "tool_text": "pikachu",
            }
        )
    )

    assert result["messages"][-1].content == "tool:PIKACHU"
    assert compiled.get_graph().nodes["summary_node"].metadata == {"tags": ["summary"]}