from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from space_game.Config import Config
from space_game.Player import Player
from space_game.events.EventProcessor import EventProcessor
from space_game.events.Event import Event
from space_game.events.PlayerDestroyedEvent import PlayerDestroyedEvent
from space_game.events.PlayerShootsEvent import PlayerShootsEvent
from space_game.events.PlayerAcceleratedEvent import PlayerAcceleratedEvent
from space_game.events.DamageDealtEvent import DamageDealtEvent
from space_game.events.creation_events.NewEventProcessorAddedEvent import NewEventProcessorAddedEvent
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
from space_game.interfaces.Registrable import Registrable
from space_game.managers.EventManager import EventManager


class RewardSystem(EventProcessor, Registrable):
    def __init__(self, environment_config: SpaceGameEnvironmentConfig, game_config: Config, agent: Player):
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
        self.environment_config = environment_config
        self.current_reward = 0.
        self.done = False

    def register(self, event_manager: EventManager):
        event_manager.add_event(NewObjectCreatedEvent(self))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), PlayerDestroyedEvent))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), PlayerAcceleratedEvent))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), DamageDealtEvent))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), PlayerShootsEvent))

    def process_event(self, event: Event):
        self.event_resolver[type(event)](event)

    def process_damage_dealt_event(self, event: DamageDealtEvent):
        if event.damaged_id == id(self.agent):
            self.current_reward += self.environment_config.taken_damage_reward
        else:
            self.current_reward += self.environment_config.target_hit_reward

    def process_player_destroyed_event(self, event: PlayerDestroyedEvent):
        if event.player_id == id(self.agent):
            self.current_reward += self.environment_config.game_lost_reward
        else:
            self.current_reward += self.environment_config.game_won_reward
        self.done = True

    def process_player_shoots_event(self, event: PlayerShootsEvent):
        if event.player_id == id(self.agent):
            self.current_reward += self.environment_config.shot_fired_reward
        self.current_reward += self.environment_config.shot_fired_reward

    def process_player_accelerated_event(self, event: PlayerAcceleratedEvent):
        if event.player_id == id(self.agent):
            self.current_reward += self.environment_config.action_taken_reward

    def get_reward_and_reset(self) -> float:
        reward = self.current_reward
        self.current_reward = 0.
        return reward

    def is_game_over(self):
        return self.done
