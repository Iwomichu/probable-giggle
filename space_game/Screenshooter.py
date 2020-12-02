import numpy as np

from pathlib import Path
from typing import Union
from uuid import uuid4

from space_game.AIActionToEventMapping import ActionIndex
from space_game.AccelerationDirection import AccelerationDirection
from space_game.Config import Config
from space_game.ai_controllers.AIController import process_map
from space_game.domain_names import ObjectId
from space_game.events.Event import Event
from space_game.events.PlayerShootsEvent import PlayerShootsEvent
from space_game.events.PlayerAcceleratedEvent import PlayerAcceleratedEvent
from space_game.events.EventProcessor import EventProcessor


class Screenshooter(EventProcessor):
    def __init__(self, config: Config, player_id: ObjectId, path: Path):
        self.config = config
        self.player_id = player_id
        self.screen_saving_path = path
        self.event_processor = {
            PlayerAcceleratedEvent: self.process_player_accelerated_event,
            PlayerShootsEvent: self.process_player_shoots,
            Event: lambda e: None
        }

    def process_event(self, event: Event):
        super().process_event(event)

    def process_player_accelerated_event(self, event: PlayerAcceleratedEvent):
        if event.player_id == self.player_id:
            if event.direction == AccelerationDirection.LEFT:
                action = ActionIndex.MoveLeft
            elif event.direction == AccelerationDirection.RIGHT:
                action = ActionIndex.MoveRight
            elif event.direction == AccelerationDirection.UP:
                action = ActionIndex.MoveUp
            elif event.direction == AccelerationDirection.DOWN:
                action = ActionIndex.MoveDown
            else:
                action = ActionIndex.StandStill

            screenshot = process_map(self.config.window)
            np.save(str(self.screen_saving_path.absolute() / str(uuid4())), (screenshot, action))

    def process_player_shoots(self, event: PlayerShootsEvent):
        if event.player_id == self.player_id:
            screenshot = process_map(self.config.window)
            np.save(str(self.screen_saving_path.absolute() / str(uuid4())), (screenshot, ActionIndex.Shoot))

