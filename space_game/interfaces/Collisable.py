from typing import Any

from space_game.domain_names import Coordinates, Shape, ObjectId


class Collisable:
    def get_coordinates(self) -> Coordinates:
        pass

    def get_shape(self) -> Shape:
        pass

    def collide(self, target_id: ObjectId) -> None:
        pass
