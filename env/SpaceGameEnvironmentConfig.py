from dataclasses import dataclass

from space_game.ai.RandomAI import RandomAI
from space_game.ai.AlwaysShootingAI import AlwaysShootingAI


@dataclass()
class SpaceGameEnvironmentConfig:
    OpponentControllerType = RandomAI
    step_reward: float = 0
    target_hit_reward: float = 15.
    shot_fired_reward: float = 0
    taken_damage_reward: float = -10
    game_lost_reward: float = -40.
    game_won_reward: float = 80.
    action_taken_reward: float = 0
    max_steps: float = 1500
