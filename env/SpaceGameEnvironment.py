import gym
import pygame
import random

from PIL import Image
from numpy import save, array

from env.EnvironmentAction import EnvironmentAction
from env.RewardSystem import RewardSystem
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from space_game.AIActionToEventMapping import AIActionToEventMapping
from space_game.Config import Config
from space_game.events.DamageDealtEvent import DamageDealtEvent
from space_game.events.PlayerAcceleratedEvent import PlayerAcceleratedEvent
from space_game.events.PlayerDestroyedEvent import PlayerDestroyedEvent
from space_game.events.PlayerShootsEvent import PlayerShootsEvent
from space_game.events.creation_events.NewEventProcessorAddedEvent import NewEventProcessorAddedEvent
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
from space_game.GameController import GameController
from space_game.Player import create_player_1, create_player_2
from space_game.ai_controllers.AIController import preprocess_map


class SpaceGameEnvironment(gym.Env):
    def __init__(self, list_of_screenshots=None, amount_of_screenshots=20, save_screenshots=False):
        super(SpaceGameEnvironment, self).__init__()
        self.amount_of_screenshots = amount_of_screenshots
        self.screenshots_left = amount_of_screenshots
        self.screenshot_count = random.randrange(100, 400)
        self.save_screenshots = save_screenshots
        if list_of_screenshots is None:
            list_of_screenshots = []
        self.list_of_screenshots = list_of_screenshots
        self.running = True
        self.clock = pygame.time.Clock()
        self.config = Config()
        self.game_controller = GameController(self.config)
        self.steps_left = SpaceGameEnvironmentConfig.max_steps
        self.agent = create_player_1(
            self.config,
            self.game_controller.event_manager
        )
        self.opponent = create_player_2(
            self.config,
            self.game_controller.event_manager
        )
        self.ai_2 = SpaceGameEnvironmentConfig.OpponentControllerType(
            self.game_controller.event_manager,
            self.config,
            self.opponent
        )
        self.game_controller.__add_player__(self.agent)
        self.history = []
        self.reward_system = RewardSystem(self.config, self.agent)
        self.game_controller.event_manager.add_event(NewObjectCreatedEvent(self.reward_system))
        self.game_controller.event_manager.add_event(NewEventProcessorAddedEvent(id(self.reward_system), PlayerDestroyedEvent))
        self.game_controller.event_manager.add_event(NewEventProcessorAddedEvent(id(self.reward_system), PlayerAcceleratedEvent))
        self.game_controller.event_manager.add_event(NewEventProcessorAddedEvent(id(self.reward_system), DamageDealtEvent))
        self.game_controller.event_manager.add_event(NewEventProcessorAddedEvent(id(self.reward_system), PlayerShootsEvent))
        self.action_space = gym.spaces.Discrete(len(AIActionToEventMapping))
        self.observation_space = gym.spaces.Box(0, 255, (80, 60))

    def reset(self):
        self.game_controller = GameController(self.config)
        self.clock = pygame.time.Clock()

        self.steps_left = SpaceGameEnvironmentConfig.max_steps

        self.agent = create_player_1(
            self.config,
            self.game_controller.event_manager
        )
        self.opponent = create_player_2(
            self.config,
            self.game_controller.event_manager
        )
        self.ai_2 = SpaceGameEnvironmentConfig.OpponentControllerType(
            self.game_controller.event_manager,
            self.config,
            self.opponent
        )
        self.game_controller.__add_player__(self.agent)
        self.game_controller.__add_player__(self.opponent)
        self.game_controller.__add_ai_controller__(self.ai_2)
        self.reward_system = RewardSystem(self.config, self.agent)
        self.game_controller.event_manager.add_event(NewObjectCreatedEvent(self.reward_system))
        self.game_controller.event_manager.add_event(NewEventProcessorAddedEvent(id(self.reward_system), PlayerDestroyedEvent))
        self.game_controller.event_manager.add_event(NewEventProcessorAddedEvent(id(self.reward_system), PlayerAcceleratedEvent))
        self.game_controller.event_manager.add_event(NewEventProcessorAddedEvent(id(self.reward_system), DamageDealtEvent))
        self.game_controller.event_manager.add_event(NewEventProcessorAddedEvent(id(self.reward_system), PlayerShootsEvent))
        return preprocess_map(self.config.window)

    def step(self, action: EnvironmentAction):
        self.screenshot_count -= 1
        if self.screenshot_count <= 0:
            print("screenshots taken")
            self.screenshot_count = random.randrange(100, 400)
            array_raw = pygame.surfarray.array3d(self.config.window)
            array_grayscale = array(Image.fromarray(array_raw).convert(mode='L').resize(size=(60, 80)))
            if self.save_screenshots:
                save(f"arr_gs{self.amount_of_screenshots-self.screenshots_left}", array_grayscale)
                save(f"arr_raw{self.amount_of_screenshots-self.screenshots_left}", array_raw)
            self.list_of_screenshots.append((array_raw, array_grayscale))
            self.screenshots_left -= 1
        if self.steps_left % 100 == 0:
            print(f"{self.steps_left} steps left!")
        self.clock.tick(self.config.fps)
        for event in AIActionToEventMapping[action](id(self.agent)):
            self.game_controller.event_manager.add_event(event)
        self.steps_left -= 1
        self.game_controller.__refresh__()
        done = self.reward_system.is_game_over()
        reward = self.reward_system.get_reward_and_reset() + SpaceGameEnvironmentConfig.step_reward
        if self.steps_left == 0:
            done = True
        self.game_controller.event_manager.process_events()
        info = {"agent_hp": self.agent.hitpoints, "opponent_hp": self.opponent.hitpoints}
        return preprocess_map(self.config.window), reward, done, info

    def render(self, mode='human'):
        pass


if __name__ == "__main__":
    from stable_baselines.deepq.policies import LnMlpPolicy
    from stable_baselines import DQN

    env = SpaceGameEnvironment()
    model = DQN(LnMlpPolicy, env, verbose=1)
    for i in range(1000):
        model.learn(total_timesteps=10**6)
        model.save("deepq_breakout")
        print("model_saved")
