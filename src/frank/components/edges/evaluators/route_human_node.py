from typing import Literal, Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from frank.entity.statehandler import StateEvaluator
from typing import Literal

class RouteHumanNode(StateEvaluator):
    def evaluate(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> Literal["end", "review"]:
        if len(state["messages"][-1].tool_calls) == 0:
            return "end"
        else:
            return "review"
