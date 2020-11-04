from typing import Tuple

from space_game.interfaces.Collisable import Collisable
from space_game.interfaces.Movable import Movable
from space_game.domain_names import Coordinate, HitPoint


class Projectile(Movable, Collisable):
    def __init__(self):
        pass

    def get_damage(self) -> HitPoint:
        pass

    def get_shape(self) -> Tuple[int, int]:
        pass

    def get_coordinates(self) -> Tuple[Coordinate, Coordinate]:
        pass

    def destroy(self) -> None:
        pass

    def update_position(self) -> None:
        pass

    def draw(self, window) -> None:
        pass

