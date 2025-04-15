from typing import Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from frank.entity.statehandler import StateEnhancer

class SimpleAsyncInvoke(StateEnhancer):
    async def enhance(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> dict[str, list]:
        messages = state["messages"]
        response = await self.runnable.ainvoke(messages)
        # We return a list, because this will get added to the existing list
        return {"messages": [response]}
