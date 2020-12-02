from collections import namedtuple
from typing import Tuple
from enum import Enum, auto

KeyId = int
Constraint = namedtuple('Constraint', ['min', 'max'])
Coordinate = float
Coordinates = Tuple[Coordinate, Coordinate]
Size = int
Shape = Tuple[Size, Size]
Acceleration = float
HitPoint = int
ObjectId = int
PlayerId = ObjectId


class Side(Enum):
    UP = auto()
    DOWN = auto()
