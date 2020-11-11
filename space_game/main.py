import pygame
import pygame.locals
import logging
from dataclasses import dataclass
from stable_baselines import DQN

from space_game.GameController import GameController
from space_game.ai_controllers.SBDQNController import SBDQNController
from space_game.events.KeyPressedEvent import KeyPressedEvent
from space_game.Config import Config
from space_game.Player import create_human_player_1, create_player_2

logger = logging.getLogger()


@dataclass()
class Assets:
    pass
    # ship_1 = pygame.image.load(os.path.join("assets", "ship_green.png"))


def main():
    running = True
    clock = pygame.time.Clock()
    config = Config()
    game_controller = GameController(config)
    player_1, p1_controller = create_human_player_1(config, game_controller.event_manager)
    dqn_model = DQN.load("../trained_models/deepq_breakout.zip")
    # player_2, p2_controller = create_human_player_2(config, game_controller.event_manager)
    player_2 = create_player_2(config, game_controller.event_manager)
    ai_2 = SBDQNController(game_controller.event_manager, config, player_2, dqn_model)
    game_controller.__add_player__(player_1, p1_controller)
    game_controller.__add_player__(player_2)
    game_controller.__add_ai_controller__(ai_2)
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


if __name__ == "__main__":
    main()
