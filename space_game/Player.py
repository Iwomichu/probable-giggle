import space_game.events.DamageDealtEvent
import space_game.events.PlayerAcceleratedEvent
from space_game.AccelerationDirection import AccelerationDirection
from space_game.events.creation_events.NewDrawableAddedEvent import NewDrawableAddedEvent
from space_game.events.creation_events.NewStatefulAddedEvent import NewStatefulAddedEvent
from space_game.interfaces.Collisable import Collisable
from space_game.Config import Config
from space_game.interfaces.Damagable import Damagable
from space_game.interfaces.Drawable import Drawable
from space_game.interfaces.Movable import Movable
from space_game.interfaces.Stateful import Stateful
from space_game.events.EventEmitter import EventEmitter
from space_game.managers.EventManager import EventManager
from space_game.events.EventProcessor import EventProcessor
from space_game.events.KeyPressedEvent import KeyPressedEvent
from space_game.events.creation_events.NewCollisableAddedEvent import NewCollisableAddedEvent
from space_game.events.creation_events.NewMovableAddedEvent import NewMovableAddedEvent
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
from space_game.events.PlayerAcceleratedEvent import PlayerAcceleratedEvent
from space_game.events.DamageDealtEvent import DamageDealtEvent
from space_game.events.Event import Event
from space_game.events.PlayerDestroyedEvent import PlayerDestroyedEvent
from space_game.KeyResolverInterface import KeyResolverInterface
from space_game.KeyProtocol import KeyProtocol
from space_game.domain_names import KeyId, Constraint, HitPoint, Coordinates, Shape, ObjectId
from space_game.Entity import Entity
from space_game.Bullet import Bullet


class Player(Movable, Damagable, Collisable, EventEmitter, EventProcessor, Drawable, Stateful):
    def __init__(self, controller_event_resolver: KeyResolverInterface, entity: Entity, hitpoints: HitPoint, config: Config, side: int, max_ammo: int, event_manager: EventManager) -> None:
        super().__init__(event_manager)
        self.controller_event_resolver = controller_event_resolver
        self.entity = entity
        self.hitpoints = hitpoints
        self.config = config
        self.side = side
        self.max_ammo = max_ammo
        self.ammo_left = self.max_ammo
        self.shoot_countdown = 0
        self.ammo_countdown = -1
        self.game_event_resolver = {
            space_game.events.KeyPressedEvent.KeyPressedEvent: self.process_key_pressed_event,
            space_game.events.PlayerAcceleratedEvent.PlayerAcceleratedEvent: self.process_acceleration_event,
            space_game.events.DamageDealtEvent.DamageDealtEvent: self.process_damage_dealt_event,
            space_game.events.Event.Event: lambda e: None
        }

    def process_event(self, event: Event):
        self.game_event_resolver.get(type(event))(event)

    def process_acceleration_event(self, event: PlayerAcceleratedEvent):
        if event.player_id == id(self):
            if event.direction == AccelerationDirection.LEFT:
                self.entity.accelerate_left()
            elif event.direction == AccelerationDirection.RIGHT:
                self.entity.accelerate_right()
            elif event.direction == AccelerationDirection.UP:
                self.entity.accelerate_up()
            elif event.direction == AccelerationDirection.DOWN:
                self.entity.accelerate_down()

    def process_damage_dealt_event(self, event: DamageDealtEvent):
        if event.damaged_id == id(self):
            self.damage(event.amount)

    def process_key_pressed_event(self, event: KeyPressedEvent):
        print(event.key_id)
        self.resolve(event.key_id)

    def damage(self, amount) -> None:
        self.hitpoints -= amount
        if self.hitpoints <= 0:
            self.event_manager.add_event(PlayerDestroyedEvent(id(self)))

    def draw(self, window) -> None:
        self.entity.draw(window)

    def update_position(self) -> None:
        self.entity.update_position()

    def shoot(self) -> None:
        if self.shoot_countdown <= 0 and self.ammo_left > 0:
            bullet = Bullet(
                    Entity(
                        self.entity.x + self.entity.width // 2,
                        self.entity.y + (self.entity.height + 5 * self.config.scale if self.side == 1 else -5 * self.config.scale),
                        None,
                        Constraint(0, self.config.width),
                        Constraint(0, self.config.height),
                        self.config.bullet_velocity * (1. if self.side == 1 else -1.),
                        0,
                        self.config.bullet_width,
                        self.config.bullet_height,
                        (
                            self.config.player_1_bullet_color
                            if self.side == 1
                            else self.config.player_2_bullet_color
                        ),
                        0.,
                        respect_constraints=False
                    ), 1, self.event_manager
                )
            self.emit_bullet_fired_events(bullet)
            self.ammo_left -= 1
        print("PEW PEW!")

    def emit_bullet_fired_events(self, bullet):
        self.event_manager.add_event(NewObjectCreatedEvent(bullet))
        self.event_manager.add_event(NewMovableAddedEvent(id(bullet)))
        self.event_manager.add_event(NewCollisableAddedEvent(id(bullet)))
        self.event_manager.add_event(NewDrawableAddedEvent(id(bullet)))
        self.event_manager.add_event(NewStatefulAddedEvent(id(bullet)))
        self.shoot_countdown = self.config.shoot_cooldown

    def resolve(self, event: KeyId) -> None:
        resolved = self.controller_event_resolver.resolve(event)
        print(resolved)
        if resolved == KeyProtocol.LEFT:
            self.entity.accelerate_left()
        elif resolved == KeyProtocol.RIGHT:
            self.entity.accelerate_right()
        elif resolved == KeyProtocol.UP:
            self.entity.accelerate_up()
        elif resolved == KeyProtocol.DOWN:
            self.entity.accelerate_down()
        elif resolved == KeyProtocol.SHOOT:
            self.shoot()

    def update_state(self):
        if self.shoot_countdown > 0:
            self.shoot_countdown -= 1
        if self.ammo_left < self.max_ammo:
            if self.ammo_countdown == -1:
                self.ammo_countdown = self.config.ammo_countdown
            elif self.ammo_countdown == 0:
                self.ammo_countdown = -1
                self.ammo_left += 1
            else:
                self.ammo_countdown -= 1

    def get_coordinates(self) -> Coordinates:
        return self.entity.get_coordinates()

    def get_shape(self) -> Shape:
        return self.entity.get_shape()

    def collide(self, target_id: ObjectId) -> None:
        pass

