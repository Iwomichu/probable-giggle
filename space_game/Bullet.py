from typing import Tuple

from space_game.interfaces.Damagable import Damagable
from space_game.interfaces.Drawable import Drawable
from space_game.Projectile import Projectile
from space_game.domain_names import Coordinate, HitPoint, ObjectId
from space_game.Entity import Entity
from space_game.events.EventEmitter import EventEmitter
from space_game.managers.EventManager import EventManager
from space_game.events.DamageDealtEvent import DamageDealtEvent
from space_game.events.ObjectDeletedEvent import ObjectDeletedEvent
from space_game.managers.ObjectsManager import objects_manager


class Bullet(Projectile, EventEmitter, Drawable):
    def __init__(self, entity: Entity, damage: HitPoint, event_manager: EventManager):
        super().__init__(event_manager)
        self.entity = entity
        self.damage = damage

    def get_damage(self) -> HitPoint:
        return self.damage

    def get_shape(self) -> Tuple[int, int]:
        return self.entity.width, self.entity.height

    def get_coordinates(self) -> Tuple[Coordinate, Coordinate]:
        return self.entity.x, self.entity.y

    def destroy(self) -> None:
        self.entity.vertical_acceleration = 0.
        self.entity.horizontal_acceleration = 0.

    def update_position(self) -> None:
        self.entity.move_horizontally()
        self.entity.move_vertically()

    def draw(self, window) -> None:
        self.entity.draw(window)

    def collide(self, target_id: ObjectId) -> None:
        if issubclass(objects_manager.get_by_id(target_id), Damagable):
            self.event_manager.add_event(DamageDealtEvent(target_id, self.damage))
            self.event_manager.add_event(ObjectDeletedEvent(id(self)))
