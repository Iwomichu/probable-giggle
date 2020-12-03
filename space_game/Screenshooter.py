import numpy as np

from pathlib import Path
from typing import Union
from time import time

from space_game.ai.AIAction import AIAction
from space_game.AccelerationDirection import AccelerationDirection
from space_game.Config import Config
from space_game.ai.AIController import process_map
from space_game.domain_names import ObjectId
from space_game.events.Event import Event
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
from space_game.events.creation_events.NewEventProcessorAddedEvent import NewEventProcessorAddedEvent
from space_game.events.PlayerShootsEvent import PlayerShootsEvent
from space_game.events.PlayerAcceleratedEvent import PlayerAcceleratedEvent
from space_game.events.EventProcessor import EventProcessor
from space_game.interfaces.Registrable import Registrable
from space_game.managers.EventManager import EventManager


class Screenshooter(EventProcessor, Registrable):
    def __init__(self, config: Config, player_id: ObjectId, path: Path):
        self.config = config
        self.player_id = player_id
        self.screen_saving_path = path
        self.event_resolver = {
            PlayerAcceleratedEvent: self.process_player_accelerated_event,
            PlayerShootsEvent: self.process_player_shoots,
            Event: lambda e: None
        }

    def register(self, event_manager: EventManager):
        event_manager.add_event(NewObjectCreatedEvent(self))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), PlayerAcceleratedEvent))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), PlayerShootsEvent))

    def process_event(self, event: Event):
        self.event_resolver[type(event)](event)

    def process_player_accelerated_event(self, event: PlayerAcceleratedEvent):
        if event.player_id == self.player_id:
            if event.direction == AccelerationDirection.LEFT:
                action = AIAction.MoveLeft
            elif event.direction == AccelerationDirection.RIGHT:
                action = AIAction.MoveRight
            elif event.direction == AccelerationDirection.UP:
                action = AIAction.MoveUp
            elif event.direction == AccelerationDirection.DOWN:
                action = AIAction.MoveDown
            else:
                action = AIAction.StandStill

            screenshot = process_map(self.config.window)
            np.save(str(self.screen_saving_path.absolute() / str(int(time()))), (screenshot, action))

    def process_player_shoots(self, event: PlayerShootsEvent):
        if event.player_id == self.player_id:
            screenshot = process_map(self.config.window)
            np.save(str(self.screen_saving_path.absolute() / str(int(time()))), (screenshot, AIAction.Shoot))

