from typing import Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from frank.entity.statehandler import StateEnhancer

class SimpleMessagesInvoke(StateEnhancer):
    """Invoke an agent runnable with the current message history.

    Reads:
        - `messages`

    Returns:
        - `messages`: a list containing the new AI response so LangGraph can
          append it to the running conversation state.
    """
    
    def enhance(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> dict[str, list]:
        messages = state["messages"]
        response = self.runnable.invoke(messages)
        # We return a list, because this will get added to the existing list
        return {"messages": [response]}
