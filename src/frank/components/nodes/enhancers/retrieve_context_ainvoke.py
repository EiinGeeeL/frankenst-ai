from typing import Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from frank.entity.statehandler import StateEnhancer

class RetrieveContextAsyncInvoke(StateEnhancer):
    """Retrieve context."""
    async def enhance(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> dict[str, list]: 
        
        if "iterations" in state and state.get("iterations", 0) > 0:
            question = state["question"]
        else:
            question = state["messages"][-1].content
        
        retrieved_docs_context = await self.runnable.ainvoke(question)

        return {"context": retrieved_docs_context, "question": question}