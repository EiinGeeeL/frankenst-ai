from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Type

class RandomMovementsProperty:
    @dataclass
    class Input(BaseModel):
        """
        Input for the RandomMovementsTool
        """
        pokemon_name: str = Field(description="The name of the pokemon that want to know random movements.")

    description: str = "This is a tool to obtain random movements of a pokemon."
    args_schema: Type[BaseModel] = Input
    return_direct: bool = True