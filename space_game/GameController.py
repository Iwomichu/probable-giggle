from typing import List
import pygame

from space_game.AccelerationDirection import AccelerationDirection
from space_game.Config import Config
from space_game.InformationDisplay import InformationDisplay
from space_game.KeyboardController import KeyboardController
from space_game.Player import Player
from space_game.Screen import Screen
from space_game.ai.AIController import AIController
from space_game.events.PlayerAcceleratedEvent import PlayerAcceleratedEvent
from space_game.events.PlayerShootsEvent import PlayerShootsEvent
from space_game.events.creation_events.NewDrawableAddedEvent import NewDrawableAddedEvent
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
from space_game.events.update_events.CheckCollisionsEvent import CheckCollisionsEvent
from space_game.events.update_events.UpdateAIControllersEvent import UpdateAIControllersEvent
from space_game.events.update_events.UpdateDrawablesEvent import UpdateDrawablesEvent
from space_game.events.update_events.UpdateMovablesEvent import UpdateMovablesEvent
from space_game.events.update_events.UpdateStatefulsEvent import UpdateStatefulsEvent
from space_game.managers.CollisionManager import CollisionManager
from space_game.managers.DrawableManager import DrawableManager
from space_game.managers.EventManager import EventManager
from space_game.managers.KeyboardEventsProcessor import KeyboardEventsProcessor
from space_game.managers.MovableManager import MovableManager
from space_game.managers.StatefulsManager import StatefulsManager


class GameController:
    def __init__(self, config: Config, renderable: bool = False):
        self.renderable = renderable
        if renderable:
            self.window = pygame.display.set_mode((config.width, config.height))
        self.config = config
        self.screen = Screen(config.width, config.height, 3)
        self.event_manager = EventManager()
        self.drawable_manager = DrawableManager(config, self.screen)
        self.collision_manager = CollisionManager(event_manager=self.event_manager)
        self.movable_manager = MovableManager()
        self.stateful_manager = StatefulsManager()
        self.keyboard_processor = KeyboardEventsProcessor(event_manager=self.event_manager)
        self.drawable_manager.register(self.event_manager)
        self.collision_manager.register(self.event_manager)
        self.movable_manager.register(self.event_manager)
        self.stateful_manager.register(self.event_manager)
        self.keyboard_processor.register(self.event_manager)
        self.players: List[Player] = []

    def __refresh__(self):
        self.event_manager.add_event(UpdateDrawablesEvent())
        self.event_manager.add_event(UpdateMovablesEvent())
        self.event_manager.add_event(UpdateStatefulsEvent())
        self.event_manager.add_event(CheckCollisionsEvent())
        self.event_manager.add_event(UpdateAIControllersEvent())

        self.event_manager.process_events()
        if self.renderable:
            self.render_screen()

    def __add_player__(self, player: Player, keyboard_controller: KeyboardController = None) -> None:
        player.register(self.event_manager)
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
            # self.__add_info__()
            pass

    def __add_info__(self):
        player_1, player_2 = self.players[:2]
        self.information_display = InformationDisplay(player_1, player_2, self.config)
        self.event_manager.add_event(NewObjectCreatedEvent(self.information_display))
        self.event_manager.add_event(NewDrawableAddedEvent(id(self.information_display)))

    def __add_ai_controller__(self, ai_controller: AIController):
        ai_controller.register(self.event_manager)

    def render_screen(self) -> None:
        surf = self.screen.convert_to_pygame_surface()
        self.window.blit(surf, (0, 0))
        pygame.display.update()
