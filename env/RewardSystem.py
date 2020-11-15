from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from space_game.Config import Config
from space_game.Player import Player
from space_game.events.EventProcessor import EventProcessor
from space_game.events.Event import Event
from space_game.events.PlayerDestroyedEvent import PlayerDestroyedEvent
from space_game.events.PlayerShootsEvent import PlayerShootsEvent
from space_game.events.PlayerAcceleratedEvent import PlayerAcceleratedEvent
from space_game.events.DamageDealtEvent import DamageDealtEvent


class RewardSystem(EventProcessor):
    def __init__(self, game_config: Config, agent: Player):
        super().__init__()
        self.agent = agent
        self.event_resolver = {
            PlayerDestroyedEvent: self.process_player_destroyed_event,
            DamageDealtEvent: self.process_damage_dealt_event,
            PlayerShootsEvent: self.process_player_shoots_event,
            PlayerAcceleratedEvent: self.process_player_accelerated_event,
            Event: lambda e: None
        }
        self.game_config = game_config
        self.current_reward = 0.
        self.done = False

    def process_event(self, event: Event):
        self.event_resolver[type(event)](event)

    def process_damage_dealt_event(self, event: DamageDealtEvent):
        if event.damaged_id == id(self.agent):
            self.current_reward += SpaceGameEnvironmentConfig.taken_damage_reward
        else:
            self.current_reward += SpaceGameEnvironmentConfig.target_hit_reward

    def process_player_destroyed_event(self, event: PlayerDestroyedEvent):
        if event.player_id == id(self.agent):
            print("Agent lost!")
            self.current_reward += SpaceGameEnvironmentConfig.game_lost_reward
        else:
            print("Agent won!")
            self.current_reward += SpaceGameEnvironmentConfig.game_won_reward
        self.done = True

    def process_player_shoots_event(self, event: PlayerShootsEvent):
        if event.player_id == id(self.agent):
            self.current_reward += SpaceGameEnvironmentConfig.shot_fired_reward
        self.current_reward += SpaceGameEnvironmentConfig.shot_fired_reward

    def process_player_accelerated_event(self, event: PlayerAcceleratedEvent):
        if event.player_id == id(self.agent):
            self.current_reward += SpaceGameEnvironmentConfig.action_taken_reward

    def get_reward_and_reset(self) -> float:
        reward = self.current_reward
        self.current_reward = 0.
        return reward

    def is_game_over(self):
        return self.done
