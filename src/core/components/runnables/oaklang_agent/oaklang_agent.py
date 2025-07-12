import logging
from typing import List
from langchain_core.prompts import (
    ChatPromptTemplate, 
    FewShotChatMessagePromptTemplate, 
    MessagesPlaceholder,
)
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_core.runnables import Runnable
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool

from .history_template import history_template
from .fewshot_examples import few_shot_examples

from frank.entity.runnable_builder import RunnableBuilder
from core.utils.common import load_and_clean_text_file

class OakLangAgent(RunnableBuilder):
    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])

    def __init__(self, model: BaseLanguageModel, tools: List[BaseTool]):
        super().__init__(model=model, tools=tools)
    
        self.logger.info("OakLangAgent initialized")

    def _build_prompt(self) -> ChatPromptTemplate:
        # Prepare the few_shot_prompt
        # few_shot_map = ChatPromptTemplate.from_messages(
        #     [
        #         ("human", "{input}"),
        #         ("ai", "{output}"),
        #     ]
        # )
        # few_shot_prompt = FewShotChatMessagePromptTemplate(
        #     example_prompt=few_shot_map,
        #     examples=few_shot_examples,
        # )

        # Prepare the prompt
        context = load_and_clean_text_file('src/core/components/runnables/oaklang_agent/prompt/context.txt')
        instructions = load_and_clean_text_file('src/core/components/runnables/oaklang_agent/prompt/instructions.txt')
        input = load_and_clean_text_file('src/core/components/runnables/oaklang_agent/prompt/input.txt')
        output_format = load_and_clean_text_file('src/core/components/runnables/oaklang_agent/prompt/output_format.txt')
        restrictions = load_and_clean_text_file('src/core/components/runnables/oaklang_agent/prompt/restrictions.txt')
                
        format_template = load_and_clean_text_file('src/core/components/runnables/oaklang_agent/prompt/format_template.txt')

        system_prompt = format_template.format(
            context=context,
            instructions=instructions,
            input=input,
            output_format=output_format,
            restrictions=restrictions
        )
        
        self.logger.info(system_prompt)

        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            # few_shot_prompt,
            history_template[0],
            MessagesPlaceholder(variable_name="messages"),
        ])

    def _configure_runnable(self) -> Runnable:
        prompt_template = self._build_prompt()
        model_with_tools = self.model.bind_tools(self.tools)

        # Create the chain
        chain = prompt_template | model_with_tools

        return chain