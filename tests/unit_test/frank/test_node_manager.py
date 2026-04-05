import asyncio

import pytest
from langgraph.prebuilt import ToolNode

from frank.entity.node import CommandNode, SimpleNode
from frank.managers.node_manager import NodeManager
from tests.support.frank_doubles.stub import (
    MissingRoutesCommander,
    RoutingCommander,
    StaticMessageEnhancer,
    uppercase_text,
)


@pytest.mark.unit
def test_add_nodes_accepts_single_and_iterable_preserving_order() -> None:
    manager = NodeManager()
    first = SimpleNode(StaticMessageEnhancer("first"), name="first")
    second = SimpleNode(StaticMessageEnhancer("second"), name="second")

    manager.add_nodes(first)
    manager.add_nodes([second])

    assert tuple(node.name for node in manager.get_nodes()) == ("first", "second")


@pytest.mark.unit
def test_add_nodes_rejects_duplicate_names() -> None:
    manager = NodeManager()
    first = SimpleNode(StaticMessageEnhancer("first"), name="same")
    duplicate = SimpleNode(StaticMessageEnhancer("second"), name="same")

    manager.add_nodes(first)

    with pytest.raises(ValueError, match="already registered"):
        manager.add_nodes(duplicate)


@pytest.mark.unit
def test_add_nodes_rejects_invalid_types() -> None:
    manager = NodeManager()

    with pytest.raises(TypeError, match="Unexpected node type"):
        manager.add_nodes("invalid")


@pytest.mark.unit
def test_command_node_requires_routes_attribute() -> None:
    with pytest.raises(ValueError, match="routes"):
        CommandNode(commander=MissingRoutesCommander(), name="invalid")


@pytest.mark.unit
def test_configs_nodes_resolve_wrapper_callables_tags_and_destinations() -> None:
    manager = NodeManager()
    simple = SimpleNode(
        enhancer=StaticMessageEnhancer("simple"),
        name="simple_node",
        tags=["simple"],
    )
    command = CommandNode(
        commander=RoutingCommander(routes={"accept": "final_node"}),
        name="command_node",
        tags=["command"],
    )
    tool_node = ToolNode([uppercase_text], name="tool_node", tags=["tool"])

    manager.add_nodes([simple, command, tool_node])
    configs = manager.configs_nodes()

    simple_name, simple_action, simple_tags, simple_destinations = configs[0]
    command_name, command_action, command_tags, command_destinations = configs[1]
    tool_name, tool_action, tool_tags, tool_destinations = configs[2]

    assert simple_name == "simple_node"
    assert simple_tags == ["simple"]
    assert simple_destinations is None
    assert asyncio.run(simple_action({"messages": []}))["messages"][-1].content == "simple"

    assert command_name == "command_node"
    assert command_tags == ["command"]
    assert command_destinations == ("final_node",)
    assert command_action({"decision": "accept"}).goto == "final_node"

    assert tool_name == "tool_node"
    assert tool_action is tool_node
    assert tool_tags == ["tool"]
    assert tool_destinations is None


@pytest.mark.unit
def test_remove_node_deletes_registered_node() -> None:
    manager = NodeManager()
    node = SimpleNode(StaticMessageEnhancer("simple"), name="simple_node")
    manager.add_nodes(node)

    manager.remove_node(node)

    assert manager.get_nodes() == ()


@pytest.mark.unit
def test_remove_node_rejects_unknown_node() -> None:
    manager = NodeManager()
    node = SimpleNode(StaticMessageEnhancer("simple"), name="simple_node")

    with pytest.raises(ValueError, match="not registered"):
        manager.remove_node(node)
