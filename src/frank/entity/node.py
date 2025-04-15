from frank.entity.statehandler import StateEnhancer, StateCommander

class BaseNode:
    def __init__(self, name: str):
        self.name = name

class SimpleNode(BaseNode):
    def __init__(
        self,
        enhancer: StateEnhancer, 
        name: str,
    ):
        super().__init__(name)
        self.enhancer = enhancer

class CommandNode(BaseNode):
    def __init__(
        self,
        commander: StateCommander,
        name: str
    ):
        super().__init__(name)
        self.commander = commander
