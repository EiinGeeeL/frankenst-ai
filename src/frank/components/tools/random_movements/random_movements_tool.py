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
from .random_movements_property import RandomMovementsProperty
from .random_movements import RandomMovements


class RandomMovementsTool(BaseTool):
    # BaseTool atributes
    name: str = None
    description: str = None
    args_schema: Type[BaseModel] = None
    return_direct: bool = None

    # New BaseTool attributes
    config: SkipValidation[RandomMovementsProperty] = RandomMovementsProperty
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

        return RandomMovements.run(pokemon_name=pokemon_name)