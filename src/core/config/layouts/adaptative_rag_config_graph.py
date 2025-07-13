from dataclasses import dataclass
from langgraph.graph import END, START
from services.ai_foundry.llm import LLMServices
from frank.entity.edge import ConditionalEdge, SimpleEdge
from frank.entity.node import SimpleNode

from core.components.runnables.multimodal_retriever.multimodal_retriever import MultimodalRetriever
from core.components.runnables.multimodal_generation.multimodal_generation import MultimodalGeneration
from core.components.runnables.structured_grade_document.structured_grade_document import StructuredGradeDocument
from core.components.runnables.rewrite_question.rewrite_question import RewriteQuestion
from core.components.edges.evaluators.grade_rewrite_generate import GradeRewriteGenerate
from core.components.nodes.enhancers.generate_answer_ainvoke import GenerateAnswerAsyncInvoke
from core.components.nodes.enhancers.retrieve_context_ainvoke import RetrieveContextAsyncInvoke
from core.components.nodes.enhancers.rewrite_question_ainvoke import RewriteQuestionAsyncInvoke
from core.models.structured_output.grade_documents import GradeDocuments
from core.utils.common import read_yaml
from core.constants import *


# NOTE: This is an example implementation for illustration purposes
# NOTE: Here you can add other subgraphs as nodes
@dataclass(frozen=True)
class AdaptativeRAGConfigGraph:
    ## Initializate LLMServices
    LLMServices.launch()

    ## RUNNABLES BUILDERS

    RETRIEVER_CHAIN = MultimodalRetriever(model=LLMServices.model, vectordb=LLMServices.vectorstore)

    GENERARION_CHAIN = MultimodalGeneration(model=LLMServices.model)

    GRADE_STRUCTURED_CHAIN = StructuredGradeDocument(model=LLMServices.model, structured_output_schema=GradeDocuments)

    REWRITE_CHAIN = RewriteQuestion(model=LLMServices.model)


    ## NODES
    CONFIG_NODES = read_yaml(CONFIG_NODES_FILE_PATH)

    GENERATION_NODE = SimpleNode(enhancer=GenerateAnswerAsyncInvoke(GENERARION_CHAIN),
                         name=CONFIG_NODES['GENERATION_NODE']['name'])
    
    RETRIEVER_NODE = SimpleNode(enhancer=RetrieveContextAsyncInvoke(RETRIEVER_CHAIN),
                        name=CONFIG_NODES['RETRIEVER_NODE']['name'])
    
    REWRITE_NODE = SimpleNode(enhancer=RewriteQuestionAsyncInvoke(REWRITE_CHAIN),
                        name=CONFIG_NODES['REWRITE_NODE']['name'])


    ## EDGES
    _EDGE_1 = SimpleEdge(node_source=START, 
                         node_path=RETRIEVER_NODE.name)
    
    _EDGE_2 = ConditionalEdge(evaluator=GradeRewriteGenerate(GRADE_STRUCTURED_CHAIN),
                              map_dict={
                                  "generate": GENERATION_NODE.name, 
                                  "rewrite": REWRITE_NODE.name, 
                                  },
                              node_source=RETRIEVER_NODE.name)

    _EDGE_3 = SimpleEdge(node_source=GENERATION_NODE.name,
                         node_path=END)     
    
    _EDGE_4 = SimpleEdge(node_source=REWRITE_NODE.name,
                         node_path=RETRIEVER_NODE.name) 
