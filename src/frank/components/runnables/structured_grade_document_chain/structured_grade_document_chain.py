import logging
from typing import Dict
from pydantic import BaseModel
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel

from frank.entity.runnable_builder import RunnableBuilder

from frank.utils.common import load_and_clean_text_file

class StructuredGradeDocument(RunnableBuilder):
    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])

    def __init__(self, model: BaseLanguageModel, structured_output_schema: BaseModel):
        super().__init__(model=model, structured_output_schema=structured_output_schema)

        self.logger.info("StructuredGradeDocument initialized")

    def _build_prompt(self, kwargs: Dict) -> ChatPromptTemplate:
        docs_by_type = kwargs["context"]
        question = kwargs["question"]

        # Prepare the human_prompt
        context = load_and_clean_text_file('src/frank/components/runnables/structured_grade_document_chain/prompt/context.txt')
        instructions = load_and_clean_text_file('src/frank/components/runnables/structured_grade_document_chain/prompt/instructions.txt')

        format_template = load_and_clean_text_file('src/frank/components/runnables/structured_grade_document_chain/prompt/format_template.txt')

        prompt_template = format_template.format(
            context=context,
            retrieved_context=docs_by_type["texts"],
            question=question,
            instructions=instructions
        )
        
        prompt_content = [{"type": "text", "text": prompt_template}]
        prompt_content.extend(docs_by_type["images"])

        return ChatPromptTemplate.from_messages([
            HumanMessage(content=prompt_content)
        ])

    def _configure_chain(self):
        structured_grade_document_chain = {
            "context": RunnableLambda(lambda kwargs: kwargs["context"]),
            "question": RunnableLambda(lambda kwargs: kwargs["question"]),
        } | RunnableLambda(self._build_prompt) | self.model.with_structured_output(schema=self.structured_output_schema, method="json_schema")

        return structured_grade_document_chain
