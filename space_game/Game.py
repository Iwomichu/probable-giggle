from pathlib import Path

import pygame
import pygame.locals
import logging

import constants
from space_game.GameController import GameController
from space_game.ai.DecisionBasedController import DecisionBasedController
from space_game.domain_names import Side
from space_game.events.KeyPressedEvent import KeyPressedEvent
from space_game.Config import Config
from space_game.Player import create_human_player_2, create_player_1, create_human_player_1, create_player_2
from space_game.Player import create_human_player_2, create_player_1
from space_game.Screenshooter import Screenshooter

logger = logging.getLogger()


def game():
    running = True
    clock = pygame.time.Clock()
    config = Config.default()
    game_controller = GameController(config, renderable=True)
    player_1, p1_controller = create_human_player_2(config, game_controller.event_manager)
    player_2 = create_player_1(config, game_controller.event_manager)
    ai_2 = DecisionBasedController(
        game_controller.event_manager,
        config,
        player_2,
        player_1,
        Side.UP,
        game_controller.screen
    )
    game_controller.__add_player__(player_2)
    game_controller.__add_player__(player_1, p1_controller)
    game_controller.__add_ai_controller__(ai_2)
    screenshooter = Screenshooter(config, id(player_1), constants.SCREENSHOTS_DIRECTORY, game_controller.screen)
    screenshooter.register(game_controller.event_manager)
    pressed_keys = {}

    while running:
        clock.tick(config.fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                print(event.key)
                pressed_keys[event.key] = True
            if event.type == pygame.KEYUP:
                pressed_keys[event.key] = False
        for key, val in pressed_keys.items():
            if val:
                game_controller.event_manager.add_event(KeyPressedEvent(key))
        game_controller.__refresh__()

    pygame.display.update()
    pygame.time.wait(5000)
