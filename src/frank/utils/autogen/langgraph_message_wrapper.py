from autogen_core import MessageContext, RoutedAgent, message_handler
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, ConfigDict
from langgraph.types import Command, RunnableConfig
from typing import List, Optional, Dict

class MessageWrapperAutogenState(BaseModel):
    content: Optional[str] = None
    command: Optional[Command] = None
    events: Optional[List[Dict]] = []
    model_config = ConfigDict(arbitrary_types_allowed=True)


class LangGraphToolUseAgent(RoutedAgent):
    def __init__(self, description: str, graph: CompiledStateGraph, runnable_config: RunnableConfig) -> None:
        super().__init__(description)
        self._app = graph
        self.runnable_config = runnable_config

    @message_handler
    async def handle_user_message(self, message: MessageWrapperAutogenState, ctx: MessageContext) -> MessageWrapperAutogenState:
        # Build input for astream depending on message type
        if isinstance(message, MessageWrapperAutogenState):
            input_data = {"messages": [{"role": "human", "content": message.content}]} if message.content else message.command 
        else:
            raise ValueError("Unsupported message type")


        event_list = message.events
        async for event in self._app.astream(input_data, self.runnable_config, stream_mode="updates"):
            event_list.append(event)
        
        # Extract the last content for output (this "get_last_event" filter_content logic inline)
        if "__interrupt__" not in event_list[-1]:
            output = event_list[-1][next(iter(event_list[-1]))]['messages'][-1].content
        else:
            output = ""

        return MessageWrapperAutogenState(content=output, events=event_list)