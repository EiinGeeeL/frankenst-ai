from langgraph.graph import MessagesState

class RAGState(MessagesState):
    """
    Represents the state of our graph.
    Attributes:
        question: query rewriter or question from the user
        context: dictionary containing texts and images
        generation: LLM generated answer
        iterations: Loop times of the process grade-rewrite-retrieve-generate
    """
    question: str
    context: dict[str, list]  # dictionary with keys: "texts" and "images" TODO: add metadata in the context
    generation: str
    iterations: int = 0