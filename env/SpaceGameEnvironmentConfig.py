from dataclasses import dataclass

from space_game.ai.AIController import AIController
from space_game.ai.RandomAI import RandomAI


@dataclass()
class SpaceGameEnvironmentConfig:
    render: bool = False
    OpponentControllerType: AIController = RandomAI
    step_reward: float = 0.
    target_hit_reward: float = 0.
    shot_fired_reward: float = 0
    taken_damage_reward: float = 0.
    game_lost_reward: float = -40.
    game_won_reward: float = 40.
    action_taken_reward: float = 0
    max_steps: float = float("inf")
    step_delay: int = 5
    shot_fired_when_on_cooldown_reward: float = 0
