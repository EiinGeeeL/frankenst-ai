from frank.entity.statehandler import StateEnhancer, StateCommander

class BaseNode:
    """Base named node definition consumed by GraphLayout and NodeManager."""

    def __init__(self, name: str):
        self.name = name

class SimpleNode(BaseNode):
    """Node wrapper for a StateEnhancer callable."""

    def __init__(
        self,
        enhancer: StateEnhancer, 
        name: str,
    ):
        super().__init__(name)
        self.enhancer = enhancer

class CommandNode(BaseNode):
    """Node wrapper for a StateCommander callable returning Command."""

    def __init__(
        self,
        commander: StateCommander,
        name: str
    ):
        super().__init__(name)
        self.commander = commander
