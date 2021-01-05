from pathlib import Path

import pygame
import pygame.locals
import logging

import constants
from space_game.GameController import GameController
from space_game.PlayerTuple import PlayerTuple
from space_game.ai.DecisionBasedController import DecisionBasedController
from space_game.domain_names import Side
from space_game.events.KeyPressedEvent import KeyPressedEvent
from space_game.Config import Config
from space_game.Player import create_human_player_1, create_player_2
from space_game.Screenshooter import Screenshooter

logger = logging.getLogger()


class Game:
    def __init__(self, config: Config):
        self.game_controller = GameController(config, renderable=True)
        self.config = config
        self.clock = pygame.time.Clock()
        self.running = True
        self.player_1_tuple = None
        self.player_2_tuple = None

    def add_player_1(self, player_1_tuple: PlayerTuple):
        self.player_1_tuple = player_1_tuple

    def add_player_2(self, player_2_tuple: PlayerTuple):
        self.player_2_tuple = player_2_tuple

    def start(self):
        if self.player_1_tuple is not None:
            player_1, p1_keyboard_controller, p1_ai_controller = \
                self.player_1_tuple.player, self.player_1_tuple.keyboard_controller, self.player_1_tuple.ai_controller
            if p1_keyboard_controller is not None:
                self.game_controller.__add_player__(player_1, p1_keyboard_controller)
            elif p1_ai_controller is not None:
                self.game_controller.__add_player__(player_1)
                self.game_controller.__add_ai_controller__(p1_ai_controller)
            else:
                raise Exception("No player 1 controller specified.")
        else:
            player_1, p1_keyboard_controller = create_human_player_1(self.config, self.game_controller.event_manager)
            self.game_controller.__add_player__(player_1, p1_keyboard_controller)

        if self.player_2_tuple is not None:
            player_2, p2_keyboard_controller, p2_ai_controller = \
                self.player_2_tuple.player, self.player_2_tuple.keyboard_controller, self.player_2_tuple.ai_controller
            if p2_keyboard_controller is not None:
                self.game_controller.__add_player__(player_2, p2_keyboard_controller)
            elif p2_ai_controller is not None:
                self.game_controller.__add_player__(player_2)
                self.game_controller.__add_ai_controller__(p2_ai_controller)
            else:
                raise Exception("No player 1 controller specified.")
        else:
            player_2 = create_player_2(self.config, self.game_controller.event_manager)
            ai_2 = DecisionBasedController(
                self.game_controller.event_manager,
                self.config,
                player_2,
                player_1,
                Side.DOWN,
                self.game_controller.screen
            )
            self.game_controller.__add_ai_controller__(ai_2)
            self.game_controller.__add_player__(player_2)

        screenshooter = Screenshooter(self.config, id(player_1), constants.SCREENSHOTS_DIRECTORY, self.game_controller.screen)
        screenshooter.register(self.game_controller.event_manager)
        pressed_keys = {}

        while self.running:
            self.clock.tick(self.config.fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    print(event.key)
                    pressed_keys[event.key] = True
                if event.type == pygame.KEYUP:
                    pressed_keys[event.key] = False
            for key, val in pressed_keys.items():
                if val:
                    self.game_controller.event_manager.add_event(KeyPressedEvent(key))
            self.game_controller.__refresh__()

        pygame.display.update()
        pygame.time.wait(5000)
