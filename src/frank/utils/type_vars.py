from dataclasses import dataclass
from typing import TypeVar

# TypeVar for the config atributes of the entities
ConfigDataclass = TypeVar('ConfigDataclass', bound=dataclass)