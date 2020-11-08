from typing import List

import pygame
import logging
from dataclasses import dataclass

from space_game.AIController import AIController
from space_game.AccelerationDirection import AccelerationDirection
from space_game.InformationDisplay import InformationDisplay
from space_game.KeyboardController import KeyboardController
from space_game.events.KeyPressedEvent import KeyPressedEvent
from space_game.events.ObjectDeletedEvent import ObjectDeletedEvent
from space_game.events.PlayerShootsEvent import PlayerShootsEvent
from space_game.events.creation_events.NewStatefulAddedEvent import NewStatefulAddedEvent
from space_game.events.update_events.UpdateAIControllersEvent import UpdateAIControllersEvent
from space_game.events.update_events.UpdateStatefulsEvent import UpdateStatefulsEvent
from space_game.managers.CollisionManager import CollisionManager
from space_game.Config import Config
from space_game.managers.DrawableManager import DrawableManager
from space_game.managers.MovableManager import MovableManager
from space_game.Player import Player, create_human_player_1, create_player_2
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
from space_game.managers.KeyboardEventsProcessor import KeyboardEventsProcessor
from space_game.RandomAI import RandomAI

logger = logging.getLogger()


@dataclass()
class Assets:
    pass
    # ship_1 = pygame.image.load(os.path.join("assets", "ship_green.png"))


class GameController:
    def __init__(self, config: Config, mode = 'human'):
        self.config = config
        self.event_manager = EventManager()
        self.drawable_manager = DrawableManager(config)
        self.collision_manager = CollisionManager(event_manager=self.event_manager)
        self.movable_manager = MovableManager()
        self.stateful_manager = StatefulsManager()
        self.keyboard_processor = KeyboardEventsProcessor(event_manager=self.event_manager)
        self.players: List[Player] = []

        self.event_manager.add_event(NewObjectCreatedEvent(self.drawable_manager))
        self.event_manager.add_event(NewObjectCreatedEvent(self.collision_manager))
        self.event_manager.add_event(NewObjectCreatedEvent(self.movable_manager))
        self.event_manager.add_event(NewObjectCreatedEvent(self.stateful_manager))
        self.event_manager.add_event(NewObjectCreatedEvent(self.keyboard_processor))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.drawable_manager), UpdateDrawablesEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.drawable_manager), NewDrawableAddedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.drawable_manager), ObjectDeletedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.collision_manager), CheckCollisionsEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.collision_manager), NewCollisableAddedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.collision_manager), ObjectDeletedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.movable_manager), UpdateMovablesEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.movable_manager), NewMovableAddedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.movable_manager), ObjectDeletedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.stateful_manager), NewStatefulAddedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.stateful_manager), UpdateStatefulsEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.stateful_manager), ObjectDeletedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(self.keyboard_processor), KeyPressedEvent))

    def __refresh__(self):
        self.event_manager.add_event(UpdateDrawablesEvent())
        self.event_manager.add_event(UpdateMovablesEvent())
        self.event_manager.add_event(UpdateStatefulsEvent())
        self.event_manager.add_event(CheckCollisionsEvent())
        self.event_manager.add_event(UpdateAIControllersEvent())

        self.event_manager.process_events()

    def __add_player__(self, player: Player, keyboard_controller: KeyboardController = None) -> None:
        self.event_manager.add_event(NewObjectCreatedEvent(player))
        self.event_manager.add_event(NewCollisableAddedEvent(id(player)))
        self.event_manager.add_event(NewDrawableAddedEvent(id(player)))
        self.event_manager.add_event(NewMovableAddedEvent(id(player)))
        self.event_manager.add_event(NewStatefulAddedEvent(id(player)))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(player), PlayerAcceleratedEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(player), DamageDealtEvent))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(player), PlayerShootsEvent))
        self.players.append(player)
        if keyboard_controller:
            self.keyboard_processor.add_new_mapping(
                keyboard_controller.LEFT,
                PlayerAcceleratedEvent(id(player), AccelerationDirection.LEFT)
            )
            self.keyboard_processor.add_new_mapping(
                keyboard_controller.RIGHT,
                PlayerAcceleratedEvent(id(player), AccelerationDirection.RIGHT)
            )
            self.keyboard_processor.add_new_mapping(
                keyboard_controller.UP,
                PlayerAcceleratedEvent(id(player), AccelerationDirection.UP)
            )
            self.keyboard_processor.add_new_mapping(
                keyboard_controller.DOWN,
                PlayerAcceleratedEvent(id(player), AccelerationDirection.DOWN)
            )
            self.keyboard_processor.add_new_mapping(
                keyboard_controller.SHOOT,
                PlayerShootsEvent(id(player))
            )
        if len(self.players) >= 2:
            self.__add_info__()

    def __add_info__(self):
        player_1, player_2 = self.players[:2]
        self.information_display = InformationDisplay(player_1, player_2, self.config)
        self.event_manager.add_event(NewObjectCreatedEvent(self.information_display))
        self.event_manager.add_event(NewDrawableAddedEvent(id(self.information_display)))

    def __add_ai_controller__(self, ai_controller: AIController):
        self.event_manager.add_event(NewObjectCreatedEvent(ai_controller))
        self.event_manager.add_event(NewEventProcessorAddedEvent(id(ai_controller), UpdateAIControllersEvent))


def main():
    running = True
    clock = pygame.time.Clock()
    config = Config()
    game_controller = GameController(config)
    player_1, p1_controller = create_human_player_1(config, game_controller.event_manager)
    # player_2, p2_controller = create_human_player_2(config, game_controller.event_manager)
    player_2 = create_player_2(config, game_controller.event_manager)
    ai_2 = RandomAI(game_controller.event_manager, config, player_2)
    game_controller.__add_player__(player_1, p1_controller)
    game_controller.__add_player__(player_2)
    game_controller.__add_ai_controller__(ai_2)
    while running:
        clock.tick(config.fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        for i, val in enumerate(pygame.key.get_pressed()):
            if val:
                print(f"Emmited {i} key press event")
                game_controller.event_manager.add_event(KeyPressedEvent(i))
        game_controller.__refresh__()

    pygame.display.update()
    pygame.time.wait(5000)


if __name__ == "__main__":
    main()
