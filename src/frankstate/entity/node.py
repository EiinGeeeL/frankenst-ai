from frankstate.entity.statehandler import StateEnhancer, StateCommander

class BaseNode:
    """Base named node definition consumed by GraphLayout and NodeManager.

    `tags` is the common user-facing annotation surface for Frankenst-AI nodes.
    Wrapper nodes forward it later to `StateGraph.add_node(metadata=...)`.
    """

    def __init__(self, name: str, tags: list[str] | None = None):
        self.name = name
        self.tags = tags

class SimpleNode(BaseNode):
    """Node wrapper for a StateEnhancer callable."""

    def __init__(
        self,
        enhancer: StateEnhancer,
        name: str,
        tags: list[str] | None = None,
    ):
        super().__init__(name, tags=tags)
        self.enhancer = enhancer

class CommandNode(BaseNode):
    """Node wrapper for a StateCommander callable returning Command."""

    def __init__(
        self,
        commander: StateCommander,
        name: str,
        tags: list[str] | None = None,
    ):
        if not hasattr(commander, "routes"):
            raise ValueError(
                f"{type(commander).__name__} must expose a 'routes: dict[str, str]' attribute "
                "where values are the registered names of destination nodes. "
                "See StateCommander docstring for the convention."
            )
        super().__init__(name, tags=tags)
        self.commander = commander

    @property
    def destinations(self) -> tuple[str, ...]:
        """Return route targets for LangGraph graph rendering.

        Reads `commander.routes` so that `add_node(destinations=...)` can draw
        edges without requiring a `Literal` annotation on the callable.
        This is only used for graph rendering and has no effect on graph execution.
        """
        return tuple(self.commander.routes.values())
