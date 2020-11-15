from typing import Dict

from space_game.Config import Config
from space_game.events.creation_events.NewEventProcessorAddedEvent import NewEventProcessorAddedEvent
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
from space_game.interfaces.Drawable import Drawable
from space_game.domain_names import ObjectId
from space_game.events.Event import Event
from space_game.events.EventProcessor import EventProcessor
from space_game.events.creation_events.NewDrawableAddedEvent import NewDrawableAddedEvent
from space_game.events.ObjectDeletedEvent import ObjectDeletedEvent
from space_game.interfaces.Registrable import Registrable
from space_game.managers.EventManager import EventManager
from space_game.managers.ObjectsManager import objects_manager
from space_game.events.update_events.UpdateDrawablesEvent import UpdateDrawablesEvent
import pygame


class DrawableManager(EventProcessor, Registrable):
    def __init__(self, config: Config, event_manager: EventManager):
        self.drawables: Dict[ObjectId, Drawable] = {}
        self.event_resolver = {
            NewDrawableAddedEvent: self.process_new_drawable_added_event,
            ObjectDeletedEvent: self.process_object_deleted_event,
            UpdateDrawablesEvent: self.process_update_drawables_event,
            Event: lambda e: None
        }
        self.config = config

    def register(self, event_manager: EventManager):
        event_manager.add_event(NewObjectCreatedEvent(self))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), NewDrawableAddedEvent))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), ObjectDeletedEvent))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), UpdateDrawablesEvent))

    def process_event(self, event: Event):
        self.event_resolver[type(event)](event)

    def process_new_drawable_added_event(self, event: NewDrawableAddedEvent):
        drawable = objects_manager.get_by_id(event.drawable_id)
        self.drawables[event.drawable_id] = drawable

    def process_object_deleted_event(self, event: ObjectDeletedEvent):
        del self.drawables[event.object_id]

    def update_drawables(self):
        self.redraw_window()
        for drawable in self.drawables.values():
            drawable.draw(self.config.window)
        pygame.display.update()

    def process_update_drawables_event(self, event: Event):
        self.update_drawables()

    def redraw_window(self):
        surface = pygame.Surface((self.config.width, self.config.height))
        surface.fill(([0, 0, 0]))
        self.config.window.blit(surface, (0, 0))
