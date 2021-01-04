from typing import Dict
from itertools import combinations

from space_game.events.creation_events.NewEventProcessorAddedEvent import NewEventProcessorAddedEvent
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
from space_game.interfaces.Collisable import Collisable
from space_game.interfaces.Registrable import Registrable
from space_game.managers.EventManager import EventManager
from space_game.managers.ObjectsManager import objects_manager
from space_game.domain_names import ObjectId
from space_game.events.update_events.CheckCollisionsEvent import CheckCollisionsEvent
from space_game.events.Event import Event
from space_game.events.EventEmitter import EventEmitter
from space_game.events.EventProcessor import EventProcessor
from space_game.events.creation_events.NewCollisableAddedEvent import NewCollisableAddedEvent
from space_game.events.CollisionOccurredEvent import CollisionOccurredEvent
from space_game.events.ObjectDeletedEvent import ObjectDeletedEvent


class CollisionManager(EventEmitter, EventProcessor, Registrable):
    def __init__(self, event_manager: EventManager):
        super().__init__(event_manager)
        self.collisables: Dict[ObjectId, Collisable] = {}
        self.event_resolver = {
            NewCollisableAddedEvent: self.process_new_collisable_added_event,
            ObjectDeletedEvent: self.process_object_deleted_event,
            CheckCollisionsEvent: self.process_check_collisions_event,
            Event: lambda e: None
        }

    def register(self, event_manager: EventManager):
        event_manager.add_event(NewObjectCreatedEvent(self))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), CheckCollisionsEvent))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), NewCollisableAddedEvent))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), ObjectDeletedEvent))

    def process_event(self, event: Event):
        self.event_resolver[type(event)](event)

    def process_new_collisable_added_event(self, event: NewCollisableAddedEvent):
        collisable = objects_manager.get_by_id(event.collisable_id)
        self.collisables[event.collisable_id] = collisable

    def process_object_deleted_event(self, event: ObjectDeletedEvent):
        if event.object_id in self.collisables:
            del self.collisables[event.object_id]

    def process_check_collisions_event(self, event: CheckCollisionsEvent):
        self.check_collisions()

    def check_collisions(self):
        for (p1_id, participant_1), (p2_id, participant_2) in combinations(self.collisables.items(), 2):
            participant_1_x, participant_1_y = participant_1.get_coordinates()
            participant_1_width, participant_1_height = participant_1.get_shape()
            if p1_id == p2_id:
                continue
            else:
                participant_2_x, participant_2_y = participant_2.get_coordinates()
                participant_2_width, participant_2_height = participant_2.get_shape()
                horizontal_collision = (participant_2_x < (participant_1_x + participant_1_width)) and (
                        (participant_2_x + participant_2_width) > participant_1_x)
                vertical_collision = (participant_2_y < (participant_1_y + participant_1_height)) and (
                        (participant_2_y + participant_2_height) > participant_1_y)
                if horizontal_collision and vertical_collision:
                    self.emit_collision(p1_id, p2_id)
                    participant_1.collide(p2_id)
                    participant_2.collide(p1_id)

    def emit_collision(self, p1_id, p2_id):
        # self.event_manager.add_event(CollisionOccurredEvent(participant_1_id=p1_id, participant_2_id=p2_id))
        pass
