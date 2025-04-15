from typing import Literal, Any, Union
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from langgraph.types import Command, interrupt

from frank.components.tools.dominate_pokemon_tool import DominatePokemonTool

from frank.entity.node import StateCommander
from frank.utils.common import read_yaml
from frank.constants import *



class HumanReviewSensitiveToolCall(StateCommander):
    config_nodes = read_yaml(CONFIG_NODES_FILE_PATH)
    
    @staticmethod
    def command(state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> Command[Literal[tuple(config_nodes['HUMAN_REVIEW_NODE']['route'].values())]]: # type: ignore
        last_message = state["messages"][-1]
        sensitive_tool_name = type(DominatePokemonTool()).__name__

        print(f"############STATE: {state}")

        print(f"############LAST_MESSAGE: {last_message}")

        if len(last_message.tool_calls) > 1:
            # Filtreting the tool_call
            # TODO: Not asume just one tool call matching
            matching_tool_calls = [tool_call for tool_call in last_message.tool_calls if tool_call['name'] == sensitive_tool_name]

            if not any(matching_tool_calls):
                return Command(goto=HumanReviewSensitiveToolCall.config_nodes['HUMAN_REVIEW_NODE']['route']['tools'])
            
            
            no_matching_tool_calls = [tool_call for tool_call in last_message.tool_calls if not tool_call['name'] == sensitive_tool_name]
            tool_call = matching_tool_calls[0]
        else:
            tool_call = last_message.tool_calls[-1]
        
        
        print(f'################TOOLS CALL: {tool_call}')
        # print(f'################MATCHING: {matching_tool_calls}')
        # print(f'#################NO MATCHING: {no_matching_tool_calls}')

        # this is the value we'll be providing via Command(resume=<human_review>) when met the condition
        human_review = interrupt(
            {
                "question": f"Are you sure to make that pokemon senstivie action to {tool_call['args']['place']}?",
                # Surface tool calls for review
                "tool_call": tool_call,
            }
        )

        # recover command after interrupt
        review_action = human_review["action"]
        review_data = human_review.get("data")

        # if approved, call the tool
        if review_action == "continue":
            return Command(goto=HumanReviewSensitiveToolCall.config_nodes['HUMAN_REVIEW_NODE']['route']['tools'])

        # # update the AI message AND call tools
        # elif review_action == "update":

        #     updated_message = {
        #         "role": "ai",
        #         "content": last_message.content,
        #         "tool_calls": [
        #             {
        #                 "id": tool_call["id"],
        #                 "name": tool_call["name"],
        #                 # This the update provided by the human
        #                 "args": review_data, # {"place" : "place"}
        #             }
        #         ],
        #         # This is important - this needs to be the same as the message you replacing!
        #         # Otherwise, it will show up as a separate message
        #         "id": last_message.id,
        #     }
            
        #     return Command(goto=HumanReviewSensitiveToolCall.config_nodes['HUMAN_REVIEW_NODE']['route']['tools'], update={"messages": [updated_message]})

        # provide feedback to LLM
        elif review_action == "feedback":
            # NOTE: we're adding feedback message as a ToolMessage
            # to preserve the correct order in the message history
            # (AI messages with tool calls need to be followed by tool call messages)

            tool_message = {
                "role": "tool",
                # This is our natural language feedback
                "content": review_data,
                "name": tool_call["name"],
                "tool_call_id": tool_call["id"],
            }
    
            return Command(goto=HumanReviewSensitiveToolCall.config_nodes['HUMAN_REVIEW_NODE']['route']['enhancer'], update={"messages": [tool_message]})
        
