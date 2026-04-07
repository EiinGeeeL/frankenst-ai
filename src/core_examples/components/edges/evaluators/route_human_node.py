from typing import Literal, Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from frankstate.entity.statehandler import StateEvaluator
from typing import Literal

class RouteHumanNode(StateEvaluator):
    """Route to human review when the latest message contains tool calls.

    Reads:
        - `messages`

    Returns:
        - `"review"` when the last assistant message includes tool calls
        - `"end"` when the graph can stop without human intervention
    """

    def evaluate(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> Literal["end", "review"]:
        if len(state["messages"][-1].tool_calls) == 0:
            return "end"
        else:
            return "review"
