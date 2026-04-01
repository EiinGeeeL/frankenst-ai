from typing import Any

from langgraph.graph import END, START
from langgraph.prebuilt import ToolNode
from langchain_core.tools import BaseTool
from services.foundry.llms import LLMServices
from frank.entity.edge import ConditionalEdge, SimpleEdge
from frank.entity.graph_layout import GraphLayout
from frank.entity.node import SimpleNode, CommandNode

from core.components.runnables.oaklang_agent.oaklang_agent import OakLangAgent
from core.components.edges.evaluators.route_human_node import RouteHumanNode
from core.components.nodes.enhancers.simple_messages_ainvoke import SimpleMessagesAsyncInvoke
from core.components.nodes.commands.human_review_sensitive_tool_call import HumanReviewSensitiveToolCall
from core.components.tools.get_evolution.get_evolution_tool import GetEvolutionTool
from core.components.tools.random_movements.random_movements_tool import RandomMovementsTool
from core.components.tools.dominate_pokemon.dominate_pokemon_tool import DominatePokemonTool
from core.utils.common import load_node_registry
from core.constants import *


# NOTE: This is an example implementation for illustration purposes
# NOTE: Here you can add other subgraphs as nodes
class OakHumanLoopConfigGraph(GraphLayout):
    """Tool-calling agent layout with an explicit human review step.

    State expectations:
        - Uses `SharedState` or another messages-compatible schema.
        - The command node inspects the latest tool call and may return a
          LangGraph `Command` with feedback updates.

    Flow:
        START -> OakLangAgent -> (HumanReview | END)
        HumanReview -> (OakTools | OakLangAgent)
        OakTools -> OakLangAgent

    Use this layout as the reference pattern for human-in-the-loop routing.
    """

    CONFIG_NODES: dict[str, Any]
    OAKLANG_AGENT: OakLangAgent
    SENSITIVE_TOOLS: list[BaseTool]

    def build_runtime(self) -> dict[str, Any]:
        LLMServices.launch()

        dominate_pokemon_tool = DominatePokemonTool()

        return {
            "CONFIG_NODES": load_node_registry(CONFIG_NODES_FILE_PATH),
            "OAKLANG_AGENT": OakLangAgent(
                model=LLMServices.model,
                tools=[GetEvolutionTool(), RandomMovementsTool(), dominate_pokemon_tool],
            ),
            "SENSITIVE_TOOLS": [dominate_pokemon_tool],
        }

    def layout(self) -> None:
        ## NODES
        self.OAKLANG_NODE = SimpleNode(
            enhancer=SimpleMessagesAsyncInvoke(self.OAKLANG_AGENT),
            name=self.CONFIG_NODES["OAKLANG_NODE"]["name"],
            tags=[self.CONFIG_NODES["OAKLANG_NODE"]["description"]],
        )
        self.OAKTOOLS_NODE = ToolNode(
            tools=self.OAKLANG_AGENT.tools,
            name=self.CONFIG_NODES["OAKTOOLS_NODE"]["name"],
            tags=[self.CONFIG_NODES["OAKTOOLS_NODE"]["description"]],
        )
        self.HUMAN_REVIEW_NODE = CommandNode(
            commander=HumanReviewSensitiveToolCall(
                sensitive_tools=self.SENSITIVE_TOOLS,
                routes=self.CONFIG_NODES["HUMAN_REVIEW_NODE"]["routes"],
            ),
            name=self.CONFIG_NODES["HUMAN_REVIEW_NODE"]["name"],
            tags=[self.CONFIG_NODES["HUMAN_REVIEW_NODE"]["description"]],
        )

        ## EDGES
        self._EDGE_1 = SimpleEdge(
            node_source=START, 
            node_path=self.OAKLANG_NODE.name)
        self._EDGE_2 = SimpleEdge(
            node_source=self.OAKTOOLS_NODE.name, 
            node_path=self.OAKLANG_NODE.name)
        self._EDGE_3 = ConditionalEdge(
            evaluator=RouteHumanNode(),
            map_dict={
                "end": END,
                "review": self.HUMAN_REVIEW_NODE.name,
            },
            node_source=self.OAKLANG_NODE.name,
        )