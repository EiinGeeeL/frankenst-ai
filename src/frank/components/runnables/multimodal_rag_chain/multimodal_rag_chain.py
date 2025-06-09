import logging
from typing import Dict
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel

from frank.entity.runnable_builder import RunnableBuilder
from frank.utils.common import load_and_clean_text_file

class MultimodalRAG(RunnableBuilder):
    logger: logging.Logger = logging.getLogger(__name__.split('.')[-1])

    def __init__(self, model: BaseLanguageModel, vectordb=None, tools=None):
        super().__init__(model, vectordb, tools)

        self.logger.info("Multimodal_RAG initialized")

    def _build_prompt(self, kwargs: Dict) -> ChatPromptTemplate:
        docs_by_type = kwargs["context"]
        question = kwargs["question"]

        # Prepare the human_prompt
        instructions = load_and_clean_text_file('src/frank/components/runnables/multimodal_rag_chain/prompt/instructions.txt')

        prompt_template = f"""{instructions}
        Context: {docs_by_type["texts"]}
        Question: {question}
        """

        prompt_content = [{"type": "text", "text": prompt_template}]
        prompt_content.extend(docs_by_type["images"])

        return ChatPromptTemplate.from_messages([
            HumanMessage(content=prompt_content)
        ])

    def _configure_chain(self):
        rag_chain = {
            "context": RunnableLambda(lambda kwargs: kwargs["context"]),
            "question": RunnableLambda(lambda kwargs: kwargs["question"]),
        } | RunnableLambda(self._build_prompt) | self.model

        return rag_chain
