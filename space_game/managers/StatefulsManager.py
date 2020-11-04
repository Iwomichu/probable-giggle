from typing import Dict

from space_game.events.creation_events.NewStatefulAddedEvent import NewStatefulAddedEvent
from space_game.events.update_events.UpdateStatefulsEvent import UpdateStatefulsEvent
from space_game.interfaces.Movable import Movable
from space_game.domain_names import ObjectId
from space_game.events.Event import Event
from space_game.events.EventProcessor import EventProcessor
from space_game.events.creation_events.NewMovableAddedEvent import NewMovableAddedEvent
from space_game.events.ObjectDeletedEvent import ObjectDeletedEvent
from space_game.interfaces.Stateful import Stateful
from space_game.managers.ObjectsManager import objects_manager
from space_game.events.update_events.UpdateMovablesEvent import UpdateMovablesEvent


class StatefulsManager(EventProcessor):
    def __init__(self):
        self.statefuls: Dict[ObjectId, Stateful] = {}
        self.event_resolver = {
            NewStatefulAddedEvent: self.process_new_stateful_added_event,
            ObjectDeletedEvent: self.process_object_deleted_event,
            UpdateStatefulsEvent: self.process_update_statefuls_event,
            Event: lambda e: None
        }

    def process_event(self, event: Event):
        self.event_resolver[type(event)](event)

    def process_new_stateful_added_event(self, event: NewStatefulAddedEvent):
        stateful = objects_manager.get_by_id(event.stateful_id)
        self.statefuls[event.stateful_id] = stateful

    def process_object_deleted_event(self, event: ObjectDeletedEvent):
        del self.statefuls[event.object_id]

    def update_statefuls(self):
        for stateful in self.statefuls.values():
            stateful.update_state()

    def process_update_statefuls_event(self, event: Event):
        self.update_statefuls()
