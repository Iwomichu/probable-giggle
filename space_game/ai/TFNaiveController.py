import numpy as np
import tensorflow as tf

from space_game.Screen import Screen
from space_game.ai.AIAction import AIAction
from space_game.ai.AIController import AIController
from space_game.Config import Config
from space_game.Player import Player
from space_game.domain_names import Side
from space_game.events.creation_events.NewEventProcessorAddedEvent import NewEventProcessorAddedEvent
from space_game.events.update_events.UpdateAIControllersEvent import UpdateAIControllersEvent
from space_game.managers.EventManager import EventManager
from space_game.ai.AIActionToEventMapping import AIActionToEventMapping


class TFNaiveController(AIController):
    def __init__(self, event_manager: EventManager, config: Config, player: Player, opponent: Player, side: Side, screen: Screen):
        super().__init__(event_manager, config, player, opponent, side, screen)
        self.model = tf.keras.models.load_model('../saved_models/tensorflow_naive')
        self.cooldown_max = 30
        self.cooldown = self.cooldown_max

    def react(self):
        if self.cooldown <= 0:
            self.cooldown = self.cooldown_max
            current_map = self.get_current_map()
            choice = np.argmax(self.model.predict(np.array([current_map])))
            for event in AIActionToEventMapping[tf_naive_action_mapper[choice]](id(self.player)):
                self.event_manager.add_event(event)
        else:
            self.cooldown -= 1

    def register(self, event_manager: EventManager):
        super().register(event_manager)
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), UpdateAIControllersEvent))


tf_naive_action_mapper = {
    0: AIAction.MoveLeft,
    1: AIAction.MoveRight,
    2: AIAction.MoveUp,
    3: AIAction.MoveDown,
    4: AIAction.Shoot,
}