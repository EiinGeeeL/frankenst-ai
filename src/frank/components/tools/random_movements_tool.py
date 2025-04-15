import requests
import random
import logging
from typing import Optional, Type
from langchain_core.tools import (
    BaseTool, 
    ToolException,
)
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, SkipValidation
from frank.entity.models.basetools.random_movements_config import RandomMovementsConfig


class RandomMovementsTool(BaseTool):
    # BaseTool atributes
    name: str = None
    description: str = None
    args_schema: Type[BaseModel] = None
    return_direct: bool = None

    # New BaseTool attributes
    config: SkipValidation[RandomMovementsConfig] = RandomMovementsConfig
    logger: SkipValidation[logging.Logger] = logging.getLogger(__name__.split('.')[-1])
     
    def __init__(self, **data):
        super().__init__(**data)
        self.name = self.__class__.__name__
        self.description = self.config.description
        self.args_schema = self.config.args_schema
        self.return_direct = self.config.return_direct
        
        
    def _run(self, pokemon_name: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> list[str]:
        """
        Run the tool logic
        """
        self.logger.info(f"Args: {pokemon_name}")

        # The url of the api
        url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}'
            
        # Make the API request
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code != 200:
            raise ToolException(f"Error: {pokemon_name} is not a valid pokemon")

        # Parse the response JSON
        data = response.json()

        # Extract the list of moves using map and lambda
        moves = list(map(lambda move: move['move']['name'], data['moves']))

        if len(moves) < 4:
            return moves

        # Select 4 random
        selected_moves = random.sample(moves, 4)

        return selected_moves