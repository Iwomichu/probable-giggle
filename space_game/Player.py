from typing import Dict, Any

import pygame

import space_game.events.DamageDealtEvent
import space_game.events.PlayerAcceleratedEvent
from space_game.AccelerationDirection import AccelerationDirection
from space_game.DictionaryKeyResolver import DictionaryKeyResolver
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
    def __init__(self, entity: Entity, hitpoints: HitPoint, config: Config, side: int, max_ammo: int, event_manager: EventManager, controller_event_resolver: DictionaryKeyResolver = None) -> None:
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
        if self.controller_event_resolver:
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


def create_player(config: Config, entity: Entity, event_manager: EventManager, side: int, event_resolver: KeyResolverInterface = None) -> Player:
    return Player(
        entity=entity,
        hitpoints=5,
        config=config,
        side=side,
        max_ammo=config.ammo_maximum,
        event_manager=event_manager,
        controller_event_resolver=event_resolver,
    )


def create_player_1(config: Config, event_manager: EventManager, key_resolver: KeyResolverInterface = None) -> Player:
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
    return create_player(config, player_1_entity, event_manager, 1, key_resolver)


def create_player_2(config: Config, event_manager: EventManager, key_resolver: KeyResolverInterface = None) -> Player:
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
    return create_player(config, player_2_entity, event_manager, 2, key_resolver)


def create_human_player_1(config: Config, event_manager: EventManager) -> Player:
    player_1_events_dictionary = {
        pygame.K_a: KeyProtocol.LEFT,
        pygame.K_d: KeyProtocol.RIGHT,
        pygame.K_w: KeyProtocol.UP,
        pygame.K_s: KeyProtocol.DOWN,
        pygame.K_SPACE: KeyProtocol.SHOOT
    }
    return create_player_1(config, event_manager, DictionaryKeyResolver(player_1_events_dictionary))


def create_human_player_2(config: Config, event_manager: EventManager) -> Player:
    player_2_events_dictionary = {
        pygame.K_LEFT: KeyProtocol.LEFT,
        pygame.K_RIGHT: KeyProtocol.RIGHT,
        pygame.K_UP: KeyProtocol.UP,
        pygame.K_DOWN: KeyProtocol.DOWN,
        pygame.K_RSHIFT: KeyProtocol.SHOOT
    }
    return create_player_2(config, event_manager, DictionaryKeyResolver(player_2_events_dictionary))
