from dataclasses import dataclass
from langgraph.graph import END, START
from langgraph.prebuilt import ToolNode
from services.llm import LLMServices
from frank.components.runnables.oaklang_agent.oaklang_agent import OakLangAgent
from frank.components.edges.evaluators.route_tool_condition import RouteToolCondition
from frank.components.nodes.enhancers.simple_ainvoke import SimpleAsyncInvoke
from frank.components.tools.get_evolution_tool import GetEvolutionTool
from frank.components.tools.random_movements_tool import RandomMovementsTool
from frank.entity.edge import ConditionalEdge, SimpleEdge
from frank.entity.node import SimpleNode
from frank.utils.common import read_yaml
from frank.constants import *

# TODO Here you can add another subgraphs as nodes

@dataclass(frozen=True)
class SimpleOakConfigGraph:
    ## RUNNABLES BUILDERS
    OAKLANG_AGENT = OakLangAgent(model=LLMServices.model,
                               tools=[GetEvolutionTool(), RandomMovementsTool()])

    ## NODES
    CONFIG_NODES = read_yaml(CONFIG_NODES_FILE_PATH)

    OAKLANG_NODE = SimpleNode(enhancer=SimpleAsyncInvoke(OAKLANG_AGENT),
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
                                  "__end__": END, # If last call `tools`, then end.
                                  "tools": OAKTOOLS_NODE.name, # Node in the loop.
                                  },
                              node_source=OAKLANG_NODE.name,)