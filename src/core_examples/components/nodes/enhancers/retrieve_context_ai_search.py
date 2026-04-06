from typing import Any, Union

from pydantic import BaseModel
from langchain_core.messages import AnyMessage

from frank.entity.statehandler import StateEnhancer


class RetrieveContextAISearch(StateEnhancer):
    """Retrieve context from Azure AI Search using the current question.

    The Azure Search retriever must be composed at layout runtime and injected
    into this enhancer. This keeps node execution focused on state transforms
    instead of infrastructure setup.

    Reads:
        - `messages` on the first retrieval pass
        - `question` and `iterations` on subsequent passes

    Returns:
        - `context`: retrieved multimodal context from AI Search
        - `question`: the question that should be used by downstream nodes
    """

    async def enhance(self, state: Union[list[AnyMessage], dict[str, Any], BaseModel]) -> dict[str, Any]:
        if "iterations" in state and state.get("iterations", 0) > 0:
            question = state["question"]
        else:
            question = state["messages"][-1].content

        retriever = getattr(self, "retriever", None)
        if retriever is None or not callable(getattr(retriever, "get_context", None)):
            raise TypeError("RetrieveContextAISearch expects an injected retriever with a callable get_context(query)")

        retrieved_docs_context = retriever.get_context(question)

        return {"context": retrieved_docs_context, "question": question}