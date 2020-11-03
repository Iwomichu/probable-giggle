import pygame
import logging
from dataclasses import dataclass

from space_game.events.creation_events.NewStatefulAddedEvent import NewStatefulAddedEvent
from space_game.events.update_events.UpdateStatefulsEvent import UpdateStatefulsEvent
from space_game.managers.CollisionManager import CollisionManager
from space_game.Config import Config
from space_game.DictionaryKeyResolver import DictionaryKeyResolver
from space_game.managers.DrawableManager import DrawableManager
from space_game.KeyProtocol import KeyProtocol
from space_game.managers.MovableManager import MovableManager
from space_game.Entity import Entity
from space_game.Player import Player
from space_game.events.update_events.CheckCollisionsEvent import CheckCollisionsEvent
from space_game.events.DamageDealtEvent import DamageDealtEvent
from space_game.managers.EventManager import EventManager
from space_game.events.creation_events.NewCollisableAddedEvent import NewCollisableAddedEvent
from space_game.events.creation_events.NewDrawableAddedEvent import NewDrawableAddedEvent
from space_game.events.creation_events.NewEventProcessorAddedEvent import NewEventProcessorAddedEvent
from space_game.events.creation_events.NewMovableAddedEvent import NewMovableAddedEvent
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
from space_game.events.PlayerAcceleratedEvent import PlayerAcceleratedEvent
from space_game.events.update_events.UpdateDrawablesEvent import UpdateDrawablesEvent
from space_game.events.update_events.UpdateMovablesEvent import UpdateMovablesEvent
from space_game.managers.StatefulsManager import StatefulsManager

logger = logging.getLogger()


@dataclass()
class Assets:
    pass
    # ship_1 = pygame.image.load(os.path.join("assets", "ship_green.png"))


def create_players(config: Config, event_manager: EventManager):
    player_1_events_dictionary = {
        pygame.K_a: KeyProtocol.LEFT,
        pygame.K_d: KeyProtocol.RIGHT,
        pygame.K_w: KeyProtocol.UP,
        pygame.K_s: KeyProtocol.DOWN,
        pygame.K_SPACE: KeyProtocol.SHOOT
    }
    player_1_entity = Entity(
        config.width / 2,
        100,
        None,
        config.player_1_width_constraint,
        config.player_1_height_constraint,
        1.,
        0.,
        config.player_size,
        config.player_size,
        config.player_1_color,
        config.max_velocity,
        config.player_acceleration
    )
    player_1 = Player(
        DictionaryKeyResolver(player_1_events_dictionary),
        player_1_entity,
        5,
        config,
        1,
        config.ammo_maximum,
        event_manager
    )

    player_2_events_dictionary = {
        pygame.K_LEFT: KeyProtocol.LEFT,
        pygame.K_RIGHT: KeyProtocol.RIGHT,
        pygame.K_UP: KeyProtocol.UP,
        pygame.K_DOWN: KeyProtocol.DOWN,
        pygame.K_RSHIFT: KeyProtocol.SHOOT
    }
    player_2_entity = Entity(
        config.width / 2,
        config.height - 100,
        None,
        config.player_2_width_constraint,
        config.player_2_height_constraint,
        -1.,
        0.,
        config.player_size,
        config.player_size,
        config.player_2_color,
        config.max_velocity,
        config.player_acceleration
    )
    player_2 = Player(
        DictionaryKeyResolver(player_2_events_dictionary),
        player_2_entity,
        5,
        config,
        2,
        config.ammo_maximum,
        event_manager
    )
    return player_1, player_2


class GameController:
    def __init__(self, config: Config):
        self.config = config
        self.event_manager = EventManager()
        self.drawable_manager = DrawableManager(config)
        self.collision_manager = CollisionManager(event_manager=self.event_manager)
        self.movable_manager = MovableManager()
        self.stateful_manager = StatefulsManager()
        player_1, player_2 = create_players(config, self.event_manager)

        self.event_manager.add_event(NewObjectCreatedEvent(self.drawable_manager))
        self.event_manager.add_event(NewObjectCreatedEvent(self.collision_manager))
        self.event_manager.add_event(NewObjectCreatedEvent(self.movable_manager))
        self.event_manager.add_event(NewObjectCreatedEvent(self.stateful_manager))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.drawable_manager), UpdateDrawablesEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.drawable_manager), NewDrawableAddedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.collision_manager), CheckCollisionsEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.collision_manager), NewCollisableAddedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.movable_manager), UpdateMovablesEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.movable_manager), NewMovableAddedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.stateful_manager), NewStatefulAddedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.stateful_manager), UpdateStatefulsEvent))

        self.event_manager.add_event(NewObjectCreatedEvent(player_1))
        self.event_manager.add_event(NewObjectCreatedEvent(player_2))
        self.event_manager.add_event(NewDrawableAddedEvent(id(player_1)))
        self.event_manager.add_event(NewDrawableAddedEvent(id(player_2)))
        self.event_manager.add_event(NewMovableAddedEvent(id(player_1)))
        self.event_manager.add_event(NewMovableAddedEvent(id(player_2)))
        self.event_manager.add_event(NewStatefulAddedEvent(id(player_1)))
        self.event_manager.add_event(NewStatefulAddedEvent(id(player_1)))
        self.event_manager.add_event(NewMovableAddedEvent(id(player_2)))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(player_1), PlayerAcceleratedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(player_1), DamageDealtEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(player_2), PlayerAcceleratedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(player_2), DamageDealtEvent))

    def __refresh__(self):
        self.event_manager.add_event(UpdateDrawablesEvent())
        self.event_manager.add_event(UpdateMovablesEvent())
        self.event_manager.add_event(UpdateStatefulsEvent())
        self.event_manager.add_event(CheckCollisionsEvent())
        self.event_manager.process_events()


def main():
    running = True
    clock = pygame.time.Clock()
    config = Config()
    game_controller = GameController(config)

    message = ""
    print(pygame.K_RSHIFT)
    while running:
        clock.tick(config.fps)
        game_controller.__refresh__()

    config.window.blit(message, (config.width // 2 - 20, config.height // 2))
    pygame.display.update()
    pygame.time.wait(5000)


if __name__ == "__main__":
    main()
