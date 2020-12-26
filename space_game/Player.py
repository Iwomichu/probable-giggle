from typing import Tuple

import pygame

from space_game.AccelerationDirection import AccelerationDirection
from space_game.KeyboardController import KeyboardController
from space_game.events.ProjectileFiredEvent import ProjectileFiredEvent
from space_game.events.creation_events.NewDrawableAddedEvent import NewDrawableAddedEvent
from space_game.events.creation_events.NewEventProcessorAddedEvent import NewEventProcessorAddedEvent
from space_game.events.creation_events.NewStatefulAddedEvent import NewStatefulAddedEvent
from space_game.interfaces.Collisable import Collisable
from space_game.Config import Config
from space_game.interfaces.Damagable import Damagable
from space_game.interfaces.Drawable import Drawable
from space_game.interfaces.Movable import Movable
from space_game.interfaces.Registrable import Registrable
from space_game.interfaces.Stateful import Stateful
from space_game.events.EventEmitter import EventEmitter
from space_game.managers.EventManager import EventManager
from space_game.events.EventProcessor import EventProcessor
from space_game.events.creation_events.NewCollisableAddedEvent import NewCollisableAddedEvent
from space_game.events.creation_events.NewMovableAddedEvent import NewMovableAddedEvent
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
from space_game.events.PlayerAcceleratedEvent import PlayerAcceleratedEvent
from space_game.events.DamageDealtEvent import DamageDealtEvent
from space_game.events.Event import Event
from space_game.events.PlayerDestroyedEvent import PlayerDestroyedEvent
from space_game.events.PlayerShootsEvent import PlayerShootsEvent
from space_game.KeyProtocol import KeyProtocol
from space_game.domain_names import Constraint, HitPoint, Coordinates, Shape, ObjectId
from space_game.Entity import Entity
from space_game.Bullet import Bullet


class Player(Movable, Damagable, Collisable, EventEmitter, EventProcessor, Drawable, Stateful, Registrable):
    def __init__(
            self,
            entity: Entity,
            hitpoints: HitPoint,
            config: Config,
            side: int,
            max_ammo: int,
            event_manager: EventManager
    ) -> None:
        super().__init__(event_manager)
        self.entity = entity
        self.hitpoints = hitpoints
        self.config = config
        self.side = side
        self.max_ammo = max_ammo
        self.ammo_left = 0
        self.shoot_countdown = 0
        self.ammo_countdown = -1
        self.game_event_resolver = {
            PlayerAcceleratedEvent: self.process_acceleration_event,
            DamageDealtEvent: self.process_damage_dealt_event,
            PlayerShootsEvent: self.process_player_shoots_event,
            Event: lambda e: None
        }

    def register(self, event_manager: EventManager):
        self.event_manager.add_event(NewObjectCreatedEvent(self))
        self.event_manager.add_event(NewCollisableAddedEvent(id(self)))
        self.event_manager.add_event(NewDrawableAddedEvent(id(self)))
        self.event_manager.add_event(NewMovableAddedEvent(id(self)))
        self.event_manager.add_event(NewStatefulAddedEvent(id(self)))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self), PlayerAcceleratedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self), DamageDealtEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self), PlayerShootsEvent))

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

    def process_player_shoots_event(self, event: PlayerShootsEvent):
        if event.player_id == id(self):
            self.shoot()

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
                        x=self.entity.x + self.entity.width // 2,
                        y=self.entity.y + (self.entity.height + 5 * self.config.scale if self.side == 1 else -5 * self.config.scale),
                        x_constraint=Constraint(0, self.config.width),
                        y_constraint=Constraint(0, self.config.height),
                        vertical_velocity=self.config.bullet_velocity * (1. if self.side == 1 else -1.),
                        horizontal_velocity=0,
                        width=self.config.bullet_width,
                        height=self.config.bullet_height,
                        color=(
                            self.config.player_1_bullet_color
                            if self.side == 1
                            else self.config.player_2_bullet_color
                        ),
                        acceleration=0.,
                        respect_constraints=False,
                        max_velocity=self.config.max_velocity
                    ), 1, self.event_manager
                )
            self.emit_bullet_fired_events(bullet)
            self.ammo_left -= 1

    def emit_bullet_fired_events(self, bullet):
        self.event_manager.add_event(NewObjectCreatedEvent(bullet))
        self.event_manager.add_event(NewMovableAddedEvent(id(bullet)))
        self.event_manager.add_event(NewCollisableAddedEvent(id(bullet)))
        self.event_manager.add_event(NewDrawableAddedEvent(id(bullet)))
        self.event_manager.add_event(NewStatefulAddedEvent(id(bullet)))
        self.event_manager.add_event(ProjectileFiredEvent(id(bullet), id(self)))
        self.shoot_countdown = self.config.shoot_cooldown

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


def create_player(config: Config, entity: Entity, event_manager: EventManager, side: int) -> Player:
    return Player(
        entity=entity,
        hitpoints=5,
        config=config,
        side=side,
        max_ammo=config.ammo_maximum,
        event_manager=event_manager
    )


def create_player_1(config: Config, event_manager: EventManager) -> Player:
    player_1_entity = Entity(
        x=config.width / 2,
        y=100,
        x_constraint=config.player_1_width_constraint,
        y_constraint=config.player_1_height_constraint,
        vertical_velocity=1.,
        horizontal_velocity=0.,
        width=config.player_size,
        height=config.player_size,
        color=config.player_1_color,
        max_velocity=config.max_velocity,
        acceleration=config.player_acceleration
    )
    return create_player(config, player_1_entity, event_manager, 1)


def create_player_2(config: Config, event_manager: EventManager) -> Player:
    player_2_entity = Entity(
        x=config.width / 2,
        y=config.height - 100,
        x_constraint=config.player_2_width_constraint,
        y_constraint=config.player_2_height_constraint,
        vertical_velocity=-1.,
        horizontal_velocity=0.,
        width=config.player_size,
        height=config.player_size,
        color=config.player_2_color,
        max_velocity=config.max_velocity,
        acceleration=config.player_acceleration
    )
    return create_player(config, player_2_entity, event_manager, 2)


def create_human_player_1(config: Config, event_manager: EventManager) -> Tuple[Player, KeyboardController]:
    player_1_keyboard_controller = KeyboardController(
        LEFT=pygame.K_a,
        RIGHT=pygame.K_d,
        UP=pygame.K_w,
        DOWN=pygame.K_s,
        SHOOT=pygame.K_SPACE
    )
    return create_player_1(config, event_manager), player_1_keyboard_controller


def create_human_player_2(config: Config, event_manager: EventManager) -> Tuple[Player, KeyboardController]:
    player_2_keyboard_controller = KeyboardController(
        LEFT=pygame.K_LEFT,
        RIGHT=pygame.K_RIGHT,
        UP=pygame.K_UP,
        DOWN=pygame.K_DOWN,
        SHOOT=pygame.K_RSHIFT
    )
    return create_player_2(config, event_manager), player_2_keyboard_controller
