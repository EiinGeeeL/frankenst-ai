import asyncio

import pytest

from tests.support.frankstate_doubles.fake import FakeRunnableBuilder, FakeVectorStore
from tests.support.frankstate_doubles.stub import (
    AsyncFieldRouteEvaluator,
    FieldRouteEvaluator,
    RoutingCommander,
    RunnableMessageEnhancer,
    SyncRunnableMessageEnhancer,
)


@pytest.mark.unit
def test_state_enhancer_injects_runnable_and_kwargs() -> None:
    builder = FakeRunnableBuilder(async_result={"content": "from-runnable"})
    enhancer = RunnableMessageEnhancer(runnable_builder=builder, marker="seen")

    result = asyncio.run(enhancer.enhance({"messages": []}))

    assert enhancer.runnable is builder.get()
    assert enhancer.marker == "seen"
    assert result["messages"][-1].content == "from-runnable"


@pytest.mark.unit
def test_state_enhancer_supports_sync_handlers() -> None:
    builder = FakeRunnableBuilder(sync_result={"content": "from-sync-runnable"})
    enhancer = SyncRunnableMessageEnhancer(runnable_builder=builder, marker="seen")

    result = enhancer.enhance({"messages": []})

    assert enhancer.runnable is builder.get()
    assert enhancer.marker == "seen"
    assert result["messages"][-1].content == "from-sync-runnable"


@pytest.mark.unit
def test_state_evaluator_injects_kwargs() -> None:
    evaluator = FieldRouteEvaluator(field="decision", marker="seen")

    assert evaluator.field == "decision"
    assert evaluator.marker == "seen"
    assert evaluator.evaluate({"decision": "accept"}) == "accept"


@pytest.mark.unit
def test_state_evaluator_supports_async_handlers() -> None:
    evaluator = AsyncFieldRouteEvaluator(field="decision", marker="seen")

    result = asyncio.run(evaluator.evaluate({"decision": "accept"}))

    assert evaluator.field == "decision"
    assert evaluator.marker == "seen"
    assert result == "accept"


@pytest.mark.unit
def test_state_commander_returns_command_with_update() -> None:
    commander = RoutingCommander(destinations={"accept": "accept_node", "reject": "reject_node"})

    command = commander.command({"decision": "reject"})

    assert command.goto == "reject_node"
    assert command.update["decision"] == "reject"
    assert command.update["messages"][-1].content == "command:reject"


@pytest.mark.unit
def test_runnable_builder_configures_runnable_once_and_delegates_calls() -> None:
    builder = FakeRunnableBuilder(sync_result="sync-result", async_result="async-result")

    assert builder.get() is builder.get()
    assert builder.configure_calls == 1
    assert builder.invoke("payload") == "sync-result"
    assert asyncio.run(builder.ainvoke("payload")) == "async-result"


@pytest.mark.unit
def test_runnable_builder_prefers_explicit_retriever() -> None:
    retriever = object()
    builder = FakeRunnableBuilder(retriever=retriever)

    assert builder.get_raw_retriever() is retriever


@pytest.mark.unit
def test_runnable_builder_builds_retriever_from_vectordb() -> None:
    retriever = object()
    vectordb = FakeVectorStore(retriever=retriever)
    builder = FakeRunnableBuilder(vectordb=vectordb)

    built = builder._build_retriever(search_type="mmr")

    assert built is retriever
    assert vectordb.calls == [{"search_type": "mmr"}]


@pytest.mark.unit
def test_runnable_builder_requires_retriever_source() -> None:
    builder = FakeRunnableBuilder(retriever=None, vectordb=None)

    with pytest.raises(ValueError, match="cannot build a retriever"):
        builder._build_retriever()
