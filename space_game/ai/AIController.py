from PIL import Image
import numpy as np
import pygame

from space_game.Config import Config
from space_game.Player import Player
from space_game.events.EventEmitter import EventEmitter
from space_game.events.EventProcessor import EventProcessor
from space_game.events.creation_events.NewEventProcessorAddedEvent import NewEventProcessorAddedEvent
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
from space_game.interfaces.Registrable import Registrable
from space_game.managers.EventManager import EventManager
from space_game.events.update_events.UpdateAIControllersEvent import UpdateAIControllersEvent
from space_game.events.Event import Event


def process_map(window) -> np.ndarray:
    array_raw = pygame.surfarray.array3d(window)
    array_processed = np.array(Image.fromarray(array_raw).resize(size=(Config.scaled_height, Config.scaled_width)))
    return array_processed


class AIController(EventEmitter, EventProcessor, Registrable):
    def __init__(self, event_manager: EventManager, config: Config, player: Player):
        super().__init__(event_manager)
        self.config = config
        self.lag = self.config.ai_input_lag
        self.lag_count_left = self.lag
        self.event_processor = {
            UpdateAIControllersEvent: self.process_update_ai_controllers_event,
            Event: lambda e: None
        }
        self.player = player

    def process_event(self, event: Event):
        if self.lag_count_left <= 0:
            self.event_processor[type(event)](event)
        else:
            self.lag_count_left -= 1

    def process_update_ai_controllers_event(self, event: UpdateAIControllersEvent):
        self.react()

    def get_current_map(self):
        return process_map(self.config.window)

    def react(self):
        """
        React to current situation on the map
        :return:
        """
        pass

    def register(self, event_manager: EventManager):
        event_manager.add_event(NewObjectCreatedEvent(self))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), UpdateAIControllersEvent))
