from dataclasses import dataclass
from langgraph.graph import END, START
from langgraph.prebuilt import ToolNode
from services.ai_foundry.llm import LLMServices
from frank.components.runnables.oaklang_agent.oaklang_agent import OakLangAgent
from frank.components.edges.evaluators.route_human_node import RouteHumanNode
from frank.components.nodes.enhancers.simple_messages_ainvoke import SimpleMessagesAsyncInvoke
from frank.components.nodes.commands.human_review_sensitive_tool_call import HumanReviewSensitiveToolCall
from frank.components.tools.get_evolution.get_evolution_tool import GetEvolutionTool
from frank.components.tools.random_movements.random_movements_tool import RandomMovementsTool
from frank.components.tools.dominate_pokemon.dominate_pokemon_tool import DominatePokemonTool
from frank.entity.edge import ConditionalEdge, SimpleEdge
from frank.entity.node import SimpleNode, CommandNode
from frank.utils.common import read_yaml
from frank.constants import *

@dataclass(frozen=True)
class OakHumanLoopConfigGraph:
    ## Initializate LLMServices
    LLMServices.launch()

    ## RUNNABLES BUILDERS
    OAKLANG_AGENT = OakLangAgent(model=LLMServices.model,
                               tools=[GetEvolutionTool(), RandomMovementsTool(), DominatePokemonTool()])

    ## NODES
    CONFIG_NODES = read_yaml(CONFIG_NODES_FILE_PATH)

    OAKLANG_NODE = SimpleNode(enhancer=SimpleMessagesAsyncInvoke(OAKLANG_AGENT),
                         name=CONFIG_NODES['OAKLANG_NODE']['name'])
     
    OAKTOOLS_NODE = ToolNode(tools=OAKLANG_AGENT.tools,
                       name=CONFIG_NODES['OAKTOOLS_NODE']['name'])

    HUMAN_REVIEW_NODE = CommandNode(commander=HumanReviewSensitiveToolCall(sensitive_tool_names=[DominatePokemonTool().name]),
                                    name=CONFIG_NODES['HUMAN_REVIEW_NODE']['name'])

    ## EDGES
    _EDGE_1 = SimpleEdge(node_source=START, 
                         node_path=OAKLANG_NODE.name)
    
    
    _EDGE_2 = SimpleEdge(node_source=OAKTOOLS_NODE.name,
                         node_path=OAKLANG_NODE.name) 

    
    _EDGE_3 = ConditionalEdge(evaluator=RouteHumanNode(),
                              map_dict={
                                  "end": END, # If last call `tools`, then end.
                                  "review": HUMAN_REVIEW_NODE.name, # Human review in the loop.
                                  },
                              node_source=OAKLANG_NODE.name,)