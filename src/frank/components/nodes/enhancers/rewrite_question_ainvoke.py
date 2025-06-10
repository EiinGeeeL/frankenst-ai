from typing import Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from frank.entity.statehandler import StateEnhancer

class RewriteQuestionAsyncInvoke(StateEnhancer):
    """Rewrite the original user question."""
    async def enhance(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> dict[str, list]: 
        question = state[ "question"]
        response = await self.runnable.ainvoke(question)
        better_question = response.content

        if "iterations" in state:
            current_iterations = state.get("iterations", 0) # default value: 0
            
            return {"messages": [response], "question": better_question, "iterations": current_iterations + 1}
        else:

            return {"messages": [response], "question": better_question}
