import logging
from typing import Dict
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable

from frank.entity.runnable_builder import RunnableBuilder
from frank.utils.common import load_and_clean_text_file

class MultimodalGeneration(RunnableBuilder):
    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])

    def __init__(self, model: BaseLanguageModel):
        super().__init__(model=model)

        self.logger.info("MultimodalGeneration initialized")

    def _build_prompt(self, kwargs: Dict) -> ChatPromptTemplate:
        docs_by_type = kwargs["context"]
        question = kwargs["question"]

        # Prepare the human_prompt
        instructions = load_and_clean_text_file('src/frank/components/runnables/multimodal_generation/prompt/instructions.txt')

        format_template = load_and_clean_text_file('src/frank/components/runnables/multimodal_generation/prompt/format_template.txt')

        prompt_template = format_template.format(
            instructions=instructions,
            retrieved_context=docs_by_type["texts"],
            question=question
        )
        
        prompt_content = [{"type": "text", "text": prompt_template}]
        prompt_content.extend(docs_by_type["images"])

        return ChatPromptTemplate.from_messages([
            HumanMessage(content=prompt_content)
        ])

    def _configure_runnable(self) -> Runnable:
        rag_chain = {
            "context": RunnableLambda(lambda kwargs: kwargs["context"]),
            "question": RunnableLambda(lambda kwargs: kwargs["question"]),
        } | RunnableLambda(self._build_prompt) | self.model

        return rag_chain
