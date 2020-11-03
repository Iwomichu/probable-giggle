from typing import Dict

from space_game.interfaces.Movable import Movable
from space_game.domain_names import ObjectId
from space_game.events.Event import Event
from space_game.events.EventProcessor import EventProcessor
from space_game.events.creation_events.NewMovableAddedEvent import NewMovableAddedEvent
from space_game.events.ObjectDeletedEvent import ObjectDeletedEvent
from space_game.managers.ObjectsManager import objects_manager
from space_game.events.update_events.UpdateMovablesEvent import UpdateMovablesEvent


class MovableManager(EventProcessor):
    def __init__(self):
        self.movables: Dict[ObjectId, Movable] = {}
        self.event_resolver = {
            NewMovableAddedEvent: self.process_new_movable_added_event,
            ObjectDeletedEvent: self.process_object_deleted_event,
            UpdateMovablesEvent: self.process_update_movables_event,
            Event: lambda e: None
        }

    def process_event(self, event: Event):
        self.event_resolver[type(event)](event)

    def process_new_movable_added_event(self, event: NewMovableAddedEvent):
        movable = objects_manager.get_by_id(event.movable_id)
        self.movables[event.movable_id] = movable

    def process_object_deleted_event(self, event: ObjectDeletedEvent):
        del self.movables[event.object_id]

    def update_movables(self):
        for movable in self.movables.values():
            movable.update_position()

    def process_update_movables_event(self, event: Event):
        self.update_movables()
