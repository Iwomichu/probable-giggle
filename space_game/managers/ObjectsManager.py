from collections import defaultdict
from typing import Any, DefaultDict

from space_game.domain_names import ObjectId
from space_game.events.Event import Event
from space_game.events.EventProcessor import EventProcessor
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
from space_game.events.ObjectDeletedEvent import ObjectDeletedEvent


class ObjectsManager(EventProcessor):
    def __init__(self):
        self.objects: DefaultDict[ObjectId, Any] = defaultdict()
        self.event_resolver = {
            NewObjectCreatedEvent: self.process_new_object_created_event,
            ObjectDeletedEvent: self.process_object_deleted_event,
            Event: lambda e: None
        }

    def process_new_object_created_event(self, event: NewObjectCreatedEvent):
        self.add_object(event.new_object)

    def process_object_deleted_event(self, event: ObjectDeletedEvent):
        self.delete_by_id(event.object_id)

    def add_object(self, o: Any):
        self.objects[id(o)] = o

    def delete_by_id(self, o_id: ObjectId):
        del self.objects[o_id]

    def process_event(self, event: Event):
        self.event_resolver.get(type(event))(event)

    def get_by_id(self, o_id: ObjectId) -> Any:
        return self.objects[o_id]


objects_manager = ObjectsManager()
