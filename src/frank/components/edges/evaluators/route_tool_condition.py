from typing import Literal, Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from frank.entity.statehandler import StateEvaluator


# NOTE: this is a class 'from langgraph.prebuilt import tools_condition'
class RouteToolCondition(StateEvaluator):
    def evaluate(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel], messages_key: str = "messages") -> Literal["end", "tools"]:
        if isinstance(state, list):
            ai_message = state[-1]
        elif isinstance(state, dict) and (messages := state.get(messages_key, [])):
            ai_message = messages[-1]
        elif messages := getattr(state, messages_key, []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return "end"