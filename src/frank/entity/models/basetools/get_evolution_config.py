from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Type

class GetEvolutionConfig:
    @dataclass
    class Input(BaseModel):
        """
        Input for the GetEvolutionTool
        """
        pokemon_name: str = Field(description="The name of the pokemon that want to know the evolutions.")

    description: str = "This is a tool to obtain the evolutions of a pokemon."
    args_schema: Type[BaseModel] = Input
    return_direct: bool = True