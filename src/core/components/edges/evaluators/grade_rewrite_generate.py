from typing import Literal, Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from frank.entity.statehandler import StateEvaluator
from typing import Literal

class GradeRewriteGenerate(StateEvaluator):
    """Determine whether the retrieved documents are relevant to the question to route to generate or rewrite"""
    async def evaluate(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> Literal["generate", "rewrite"]:
    
        question = state["question"]
        context = state["context"]
        
        response = await self.runnable.ainvoke({
            "context": context,
            "question": question
        })
        
        score = response.binary_score

        if score == "yes" or state.get("iterations", 0) >= 1:
            return "generate"
        else:
            return "rewrite"