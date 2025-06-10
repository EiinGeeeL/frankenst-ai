from typing import Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from frank.entity.statehandler import StateEnhancer

class GenerateAnswerAsyncInvoke(StateEnhancer):
    """Generate the answer of a question."""
    async def enhance(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> dict[str, list]: 
        response = await self.runnable.ainvoke({
            "context": state["context"],
            "question": state["question"]
            })
    
        return {"messages": [response], "generation": response.content}