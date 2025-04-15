from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Type

class DominatePokemonConfig:
    @dataclass
    class Input(BaseModel):
        """
        Input for the DominatePokemonTool
        """
        place: str = Field(description="Place could be a city, country or continent")

    description: str = "This is a tool that move trainers to capture or dominate all the pokemon of a certain place. Return a youtube url to see the effect of that action."
    args_schema: Type[BaseModel] = Input
    return_direct: bool = True