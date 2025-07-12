from pydantic import BaseModel
from typing import Type

class LangChainToolProperty:
    def __init__(
        self,
        input: Type[BaseModel],
        description: str,
        return_direct: bool = True,
    ):
        self.args_schema: Type[BaseModel] = input
        self.description: str = description
        self.return_direct: bool = return_direct
