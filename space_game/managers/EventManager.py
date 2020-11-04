from typing import Dict, Deque, DefaultDict, Any
from collections import deque, defaultdict

from space_game.domain_names import ObjectId
from space_game.events.EventProcessor import EventProcessor
from space_game.events.Event import Event
from space_game.managers.ObjectsManager import objects_manager
from space_game.events.creation_events.NewEventProcessorAddedEvent import NewEventProcessorAddedEvent
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
from space_game.events.ObjectDeletedEvent import ObjectDeletedEvent


class EventManager(EventProcessor):
    def __init__(self):
        self.event_processors: DefaultDict[Any, Dict[ObjectId, EventProcessor]] = defaultdict(dict)
        self.event_queue: Deque[Event] = deque()
        self.event_processors[ObjectDeletedEvent][id(self)] = self
        self.event_processors[NewEventProcessorAddedEvent][id(self)] = self
        self.event_processors[NewObjectCreatedEvent][id(objects_manager)] = objects_manager
        self.event_processors[ObjectDeletedEvent][id(objects_manager)] = objects_manager
        self.event_resolver = {
            ObjectDeletedEvent: self.process_object_deleted_event,
            NewEventProcessorAddedEvent: self.process_new_event_processor_added_event,
            Event: lambda e: None
        }

    def process_events(self) -> None:
        while len(self.event_queue) > 0:
            event = self.event_queue.popleft()
            for processor in self.event_processors[type(event)].values():
                processor.process_event(event)

    def process_event(self, event: Event):
        self.event_resolver[type(event)](event)

    def process_object_deleted_event(self, event: ObjectDeletedEvent):
        for sub_dict in self.event_processors.values():
            if event.object_id in sub_dict:
                del sub_dict[event.object_id]

    def process_new_event_processor_added_event(self, event: NewEventProcessorAddedEvent):
        self.add_event_processor(event.processor_id, event.event_type)

    def add_event(self, event: Event):
        self.event_queue.append(event)

    def add_event_processor(self, event_processor_id: ObjectId, event_type: Any):
        event_processor = objects_manager.get_by_id(event_processor_id)
        self.event_processors[event_type][event_processor_id] = event_processor
