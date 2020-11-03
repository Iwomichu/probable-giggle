from collections import namedtuple
from typing import Tuple

KeyId = int
Constraint = namedtuple('Constraint', ['min', 'max'])
Coordinate = float
Coordinates = Tuple[Coordinate, Coordinate]
Size = int
Shape = Tuple[Size, Size]
Acceleration = float
HitPoint = int
ObjectId = int
