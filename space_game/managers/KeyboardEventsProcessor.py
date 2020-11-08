from typing import DefaultDict, List, Any
from collections import defaultdict

from space_game.events.Event import Event
from space_game.events.KeyPressedEvent import KeyPressedEvent
from space_game.events.EventEmitter import EventEmitter
from space_game.events.EventProcessor import EventProcessor
from space_game.managers.EventManager import EventManager


class KeyboardEventsProcessor(EventProcessor, EventEmitter):
    def __init__(self, event_manager: EventManager):
        super().__init__(event_manager)
        self.key_to_event_mappings: DefaultDict[Any, List[Event]] = defaultdict(list)
        self.event_resolver = {
            KeyPressedEvent: self.process_key_pressed_event,
            Event: lambda e: None
        }

    def add_new_mapping(self, key: Any, event: Event):
        self.key_to_event_mappings[key].append(event)

    def process_key_pressed_event(self, event: KeyPressedEvent):
        for map_event in self.key_to_event_mappings.get(event.key_id):
            self.event_manager.add_event(map_event)

    def process_event(self, event: Event):
        self.event_resolver.get(type(event))(event)
