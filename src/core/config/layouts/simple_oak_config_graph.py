from dataclasses import dataclass
from langgraph.graph import END, START
from langgraph.prebuilt import ToolNode
from services.ai_foundry.llm import LLMServices
from frank.entity.edge import ConditionalEdge, SimpleEdge
from frank.entity.node import SimpleNode

from core.components.runnables.oaklang_agent.oaklang_agent import OakLangAgent
from core.components.edges.evaluators.route_tool_condition import RouteToolCondition
from core.components.nodes.enhancers.simple_messages_ainvoke import SimpleMessagesAsyncInvoke
from core.components.tools.get_evolution.get_evolution_tool import GetEvolutionTool
from core.components.tools.random_movements.random_movements_tool import RandomMovementsTool
from core.utils.common import read_yaml
from core.constants import *


# NOTE: This is an example implementation for illustration purposes
# NOTE: Here you can add other subgraphs as nodes
@dataclass(frozen=True)
class SimpleOakConfigGraph:
    ## Initializate LLMServices
    LLMServices.launch()

    ## RUNNABLES BUILDERS
    OAKLANG_AGENT = OakLangAgent(model=LLMServices.model,
                               tools=[GetEvolutionTool(), RandomMovementsTool()])

    ## NODES
    CONFIG_NODES = read_yaml(CONFIG_NODES_FILE_PATH)

    OAKLANG_NODE = SimpleNode(enhancer=SimpleMessagesAsyncInvoke(OAKLANG_AGENT),
                         name=CONFIG_NODES['OAKLANG_NODE']['name'])
     
    OAKTOOLS_NODE = ToolNode(tools=OAKLANG_AGENT.tools,
                       name=CONFIG_NODES['OAKTOOLS_NODE']['name'])

    ## EDGES
    _EDGE_1 = SimpleEdge(node_source=START, 
                         node_path=OAKLANG_NODE.name)
    
    
    _EDGE_2 = SimpleEdge(node_source=OAKTOOLS_NODE.name,
                         node_path=OAKLANG_NODE.name) 

    
    _EDGE_3 = ConditionalEdge(evaluator=RouteToolCondition(),
                              map_dict={
                                  "end": END, # If last call `tools`, then end.
                                  "tools": OAKTOOLS_NODE.name, # Node in the loop.
                                  },
                              node_source=OAKLANG_NODE.name,)