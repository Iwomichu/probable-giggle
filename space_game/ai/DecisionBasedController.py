from typing import Dict, List, Union
from random import randint

from space_game.ai.AIActionToEventMapping import AIActionToEventMapping
from space_game.Config import Config
from space_game.Player import Player
from space_game.Projectile import Projectile
from space_game.ai.AIAction import AIAction
from space_game.ai.AIController import AIController
from space_game.domain_names import ObjectId, Side
from space_game.events.Event import Event
from space_game.events.creation_events.NewEventProcessorAddedEvent import NewEventProcessorAddedEvent
from space_game.events.creation_events.NewObjectCreatedEvent import NewObjectCreatedEvent
from space_game.managers.EventManager import EventManager
from space_game.events.ProjectileFiredEvent import ProjectileFiredEvent
from space_game.events.ObjectDeletedEvent import ObjectDeletedEvent
from space_game.managers.ObjectsManager import objects_manager


def random_vertical_action_modifier() -> Union[AIAction, bool]:
    random_number = randint(0, 9)
    if random_number <= 2:
        return AIAction.MoveUp
    if random_number >= 8:
        return AIAction.MoveDown
    else:
        return AIAction.StandStill


def shooting_modifier() -> AIAction:
    return AIAction.Shoot


class DecisionBasedController(AIController):
    def __init__(self, event_manager: EventManager, config: Config, player: Player, opponent: Player, side: Side):
        super().__init__(event_manager, config, player)
        self.opponent = opponent
        self.interaction_margin = 10
        self.side = side
        self.reaction_distance = 200 if self.side == Side.UP else -200
        self.critical_distance = 100 if self.side == Side.UP else -100
        self.is_dodging = False
        self.is_following = True
        self.tracked_projectiles: Dict[ObjectId, Projectile] = {}
        self.event_processor = {
            ProjectileFiredEvent: self.process_projectile_fired_event,
            ObjectDeletedEvent: self.process_object_deleted_event,
            **self.event_processor
        }

    def react(self):
        # 1. if projectile in critical -> dodge and ignore everything else
        # 2. if multiple projectiles in irs -> move to side with fewer of them unless 1.
        # 3. if single projectile in irs -> dont move in its direction unless 1.
        # 4. if opponent in interaction site -> shoot
        projectiles_in_irs = self.get_projectiles_in_irs()
        choice = AIAction.StandStill
        if self.projectile_in_critical():
            choice += self.dodge_critical_projectile()
        elif projectiles_in_irs:
            choice += self.dodge_projectiles(projectiles_in_irs)
        else:
            choice += self.move_toward_opponent()
        choice +=  random_vertical_action_modifier()
        if self.is_opponent_in_interaction_site():
            choice += AIAction.Shoot
        for event in AIActionToEventMapping[choice](id(self.player)):
            self.event_manager.add_event(event)

    def process_event(self, event: Event) -> None:
        if self.lag_count_left <= 0:
            self.event_processor[type(event)](event)
        else:
            self.lag_count_left -= 1

    def process_projectile_fired_event(self, event: ProjectileFiredEvent) -> None:
        if event.shooter_id == id(self.opponent):
            self.tracked_projectiles[event.projectile_id] = objects_manager.get_by_id(event.projectile_id)

    def process_object_deleted_event(self, event: ObjectDeletedEvent) -> None:
        if event.object_id in self.tracked_projectiles:
            del self.tracked_projectiles[event.object_id]

    def projectile_in_critical(self) -> bool:
        player_x, player_y = self.player.get_coordinates()
        player_width = self.player.entity.width
        for projectile in self.tracked_projectiles.values():
            projectile_x, projectile_y = projectile.get_coordinates()
            horizontal = player_x < projectile_x < player_x + player_width
            vertical = player_y + self.critical_distance < projectile_y
            if vertical and horizontal:
                return True
        else:
            return False

    def get_projectiles_in_irs(self) -> List[Projectile]:
        return sorted(
            [
                projectile
                for projectile in self.tracked_projectiles.values()
                if self.is_projectile_in_irs(projectile)]
            , key=lambda p: p.get_shape()[0]
        )

    def is_projectile_in_irs(self, projectile: Projectile) -> bool:
        player_x, player_y = self.player.get_coordinates()
        player_width = self.player.entity.width
        projectile_x, projectile_y = projectile.get_coordinates()
        horizontal = player_x - self.interaction_margin < projectile_x < player_x + player_width + self.interaction_margin
        vertical = player_y + self.reaction_distance > projectile_y
        return vertical and horizontal

    def is_opponent_in_interaction_site(self) -> bool:
        player_x, player_y = self.player.get_coordinates()
        player_width = self.player.entity.width
        opponent_x, opponent_y = self.opponent.get_coordinates()
        opponent_width = self.opponent.entity.width
        return player_x - self.interaction_margin < opponent_x < player_x + player_width + opponent_width + self.interaction_margin

    def dodge_projectiles(self, projectiles_in_irs: List[Projectile]):
        distances = [
            min(
                abs(self.player.get_coordinates()[0] - projectile.get_coordinates()[0]),
                abs(self.player.entity.get_coordinates()[0] + self.player.entity.width - projectile.get_coordinates()[0])
            ) for projectile in projectiles_in_irs
        ]
        closest_index = min(range(len(distances)), key=lambda k: distances[k])
        direction_of_dodging = AIAction.MoveLeft if closest_index - len(distances)/2 < 0 else AIAction.MoveRight
        return direction_of_dodging

    def dodge_critical_projectile(self) -> AIAction:
        if self.player.entity.horizontal_velocity > 0.:
            return AIAction.MoveRight
        else:
            return AIAction.MoveLeft

    def register(self, event_manager: EventManager):
        super().register(event_manager)
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), ProjectileFiredEvent))
        event_manager.add_event(NewEventProcessorAddedEvent(id(self), ObjectDeletedEvent))

    def move_toward_opponent(self):
        player_x, player_y = self.player.get_coordinates()
        opponent_x, opponent_y = self.opponent.get_coordinates()
        if player_x - opponent_x > 0:
            return AIAction.MoveLeft
        else:
            return AIAction.MoveRight
