from typing import Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from frank.entity.statehandler import StateEnhancer

class GenerateAnswerAsyncInvoke(StateEnhancer):
    """Generate the final answer for the current retrieval iteration.

    Reads:
        - `context`
        - `question`

    Returns:
        - `messages`: a list containing the final AI response
        - `generation`: the response content stored as a scalar graph field
    """

    async def enhance(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> dict[str, list]: 
        response = await self.runnable.ainvoke({
            "context": state["context"],
            "question": state["question"]
            })
    
        return {"messages": [response], "generation": response.content}