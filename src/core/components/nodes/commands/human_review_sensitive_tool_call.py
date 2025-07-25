from typing import Literal, Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from langgraph.types import Command, interrupt

from frank.entity.node import StateCommander
from core.utils.common import read_yaml
from core.constants import *


class HumanReviewSensitiveToolCall(StateCommander):
    config_nodes: dict[str, dict[str, dict[str, str]]] = read_yaml(CONFIG_NODES_FILE_PATH)
    
    def __init__(self, sensitive_tool_names: list[str] = None):
        """
        Load Sensitive tool names list
        """
        self.sensitive_tool_names = sensitive_tool_names or []
    
    def command(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> Command[Literal[tuple(config_nodes['HUMAN_REVIEW_NODE']['route'].values())]]: # type: ignore
        last_message = state["messages"][-1]
        # Separate sensitive and non-sensitive tool calls
        sensitive_calls = [
            tool_call for tool_call in last_message.tool_calls
            if tool_call["name"] in self.sensitive_tool_names
        ]
        
        # If no sensitive tools, run all tools immediately
        if not sensitive_calls:
            return Command(goto=self.config_nodes['HUMAN_REVIEW_NODE']['route']['tools'])

        # Get the *first* sensitive tool call to ask for review and update
        tool_call = sensitive_calls[0]

        # Interrupt and ask human for feedback
        human_review = interrupt({
            "question": f"Are you sure you want to proceed with this sensitive action for {tool_call["args"]}?",
            "tool_call": tool_call,
        })

        review_action = human_review["action"]
        review_data = human_review.get("data")

        if review_action == "continue":
            return Command(goto=self.config_nodes['HUMAN_REVIEW_NODE']['route']['tools'])

        elif review_action == "feedback":
            # ToolMessage for sensitive tool feedback
            feedback_tool_message = {
                "role": "tool",
                "content": review_data,
                "name": tool_call["name"],
                "tool_call_id": tool_call["id"],
            }

            # Return in same order as original tool_calls
            all_tool_messages = []

            for call in last_message.tool_calls:
                if call["id"] == tool_call["id"]:
                    all_tool_messages.append(feedback_tool_message)
                else:
                    # passthrough (empty response for untouched tools)
                    all_tool_messages.append({
                        "role": "tool",
                        "content": "",
                        "name": call["name"],
                        "tool_call_id": call["id"],
                    })

            return Command(goto=self.config_nodes['HUMAN_REVIEW_NODE']['route']['enhancer'], update={"messages": all_tool_messages})

