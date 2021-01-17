from dataclasses import dataclass
from pathlib import Path
from typing import Type

from yaml import safe_load, YAMLError

from constants import CONFIGS_DIRECTORY
from space_game.ai.AIController import AIController
from space_game.ai.DecisionBasedController import DecisionBasedController
from space_game.ai.RandomAI import RandomAI


@dataclass()
class SpaceGameEnvironmentConfig:
    render: bool = False
    OpponentControllerType: Type[AIController] = RandomAI
    step_reward: float = 0.
    target_hit_reward_start: float = 0.
    target_hit_reward_end: float = 0.
    target_hit_reward_decay: float = 0.
    shot_fired_reward: float = 0
    taken_damage_reward_start: float = 0.
    taken_damage_reward_end: float = 0.
    taken_damage_reward_decay: float = 0.
    game_lost_reward_start: float = -40.
    game_lost_reward_end: float = -40.
    game_lost_reward_decay: float = 0
    game_won_reward_start: float = 40.
    game_won_reward_end: float = 40.
    game_won_reward_decay: float = 0
    action_taken_reward: float = 0
    max_steps: float = float("inf")
    step_delay: int = 5
    shot_fired_when_on_cooldown_reward: float = 0
    use_simplified_environment_actions: bool = False
    hit_reward_decay: float = 0.
    game_result_reward_increase: float = 1.

    @staticmethod
    def from_config_dict(config_dict: dict):
        return SpaceGameEnvironmentConfig(
            render=config_dict['render'],
            max_steps=config_dict['max_steps'],
            OpponentControllerType=OpponentTypeStringToTypeDict.get(config_dict['opponent_controller_type']),
            shot_fired_reward=config_dict['reward']['shot_fired'],
            step_reward=config_dict['reward']['step'],
            game_won_reward_start=config_dict['reward']['game_won']['start'],
            game_won_reward_end=config_dict['reward']['game_won']['end'],
            game_won_reward_decay=config_dict['reward']['game_won']['decay'],
            game_lost_reward_start=config_dict['reward']['game_lost']['start'],
            game_lost_reward_end=config_dict['reward']['game_lost']['end'],
            game_lost_reward_decay=config_dict['reward']['game_lost']['decay'],
            action_taken_reward=config_dict['reward']['action_taken'],
            shot_fired_when_on_cooldown_reward=config_dict['reward']['shot_fired_when_on_cooldown'],
            taken_damage_reward_start=config_dict['reward']['taken_damage']['start'],
            taken_damage_reward_end=config_dict['reward']['taken_damage']['end'],
            taken_damage_reward_decay=config_dict['reward']['taken_damage']['decay'],
            target_hit_reward_start=config_dict['reward']['target_hit']['start'],
            target_hit_reward_end=config_dict['reward']['target_hit']['end'],
            target_hit_reward_decay=config_dict['reward']['target_hit']['decay'],
            use_simplified_environment_actions=config_dict['use_simplified_environment_actions']
        )

    @staticmethod
    def default():
        with open(CONFIGS_DIRECTORY / "gym_api_env_config.default.yml", 'r') as f:
            try:
                config_file = safe_load(f)
                return SpaceGameEnvironmentConfig.from_config_dict(config_file)
            except YAMLError as exc:
                print("gym api env config loading failed. stacktrace:")
                print(exc)

    @staticmethod
    def unified():
        return SpaceGameEnvironmentConfig.custom(CONFIGS_DIRECTORY / "unified_gym_api_env_config.yml")

    @staticmethod
    def custom(path: Path):
        with open(path, 'r') as f:
            try:
                config_file = safe_load(f)
                return SpaceGameEnvironmentConfig.from_config_dict(config_file)
            except YAMLError as exc:
                print("gym api env config loading failed. stacktrace:")
                print(exc)


OpponentTypeStringToTypeDict = {
    "RandomAI": RandomAI,
    "DecisionBasedController": DecisionBasedController
}
