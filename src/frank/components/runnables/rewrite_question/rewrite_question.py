import logging
from typing import Dict
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable

from frank.entity.runnable_builder import RunnableBuilder
from frank.utils.common import load_and_clean_text_file

class RewriteQuestion(RunnableBuilder):
    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])

    def __init__(self, model: BaseLanguageModel):
        super().__init__(model=model)

        self.logger.info("RewiteQuestion initialized")

    def _build_prompt(self, kwargs: Dict) -> ChatPromptTemplate:
        question = kwargs["question"]

        # Prepare the human_prompt
        format_template = load_and_clean_text_file('src/frank/components/runnables/rewrite_question/prompt/format_template.txt')

        prompt_template = format_template.format(
            question=question
        )
        
        prompt_content = [{"type": "text", "text": prompt_template}]

        return ChatPromptTemplate.from_messages([
            HumanMessage(content=prompt_content)
        ])

    def _configure_runnable(self) -> Runnable:
        rewrite_chain = {
            "question": RunnablePassthrough(),
        } | RunnableLambda(self._build_prompt) | self.model

        return rewrite_chain