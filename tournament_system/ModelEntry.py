from dataclasses import dataclass
from typing import Any


ModelID = int
ModelInstance = Any


@dataclass
class ModelEntry:
    id: ModelID
    model: ModelInstance
