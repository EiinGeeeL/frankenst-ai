from typing import Literal, Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from frankstate.entity.statehandler import StateEvaluator
from typing import Literal

class GradeRewriteGenerate(StateEvaluator):
    """Choose between answer generation and question rewriting.

    Reads:
        - `question`
        - `context`
        - `iterations`

    Returns:
        - `"generate"` when the retrieved context is relevant or the graph has
            already retried enough times
        - `"rewrite"` when the question should be refined before another
            retrieval attempt
    """

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