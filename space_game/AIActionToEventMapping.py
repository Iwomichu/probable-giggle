from typing import List, Callable
from enum import Enum

from space_game.events.PlayerAcceleratedEvent import PlayerAcceleratedEvent
from space_game.events.PlayerShootsEvent import PlayerShootsEvent
from space_game.AccelerationDirection import AccelerationDirection
from space_game.events.Event import Event
from space_game.domain_names import PlayerId


AIActionToEventMapping: List[Callable[[PlayerId], List[Event]]] = [
    lambda player_id: [PlayerShootsEvent(player_id)],
    lambda player_id: [PlayerAcceleratedEvent(player_id, AccelerationDirection.LEFT)],
    lambda player_id: [PlayerAcceleratedEvent(player_id, AccelerationDirection.RIGHT)],
    lambda player_id: [PlayerAcceleratedEvent(player_id, AccelerationDirection.UP)],
    lambda player_id: [PlayerAcceleratedEvent(player_id, AccelerationDirection.DOWN)],

    lambda player_id: AIActionToEventMapping[1](player_id) + AIActionToEventMapping[3](player_id),
    lambda player_id: AIActionToEventMapping[1](player_id) + AIActionToEventMapping[4](player_id),
    lambda player_id: AIActionToEventMapping[2](player_id) + AIActionToEventMapping[3](player_id),
    lambda player_id: AIActionToEventMapping[2](player_id) + AIActionToEventMapping[4](player_id),

    lambda player_id: AIActionToEventMapping[1](player_id) + AIActionToEventMapping[0](player_id),
    lambda player_id: AIActionToEventMapping[2](player_id) + AIActionToEventMapping[0](player_id),
    lambda player_id: AIActionToEventMapping[3](player_id) + AIActionToEventMapping[0](player_id),
    lambda player_id: AIActionToEventMapping[4](player_id) + AIActionToEventMapping[0](player_id),
    lambda player_id: AIActionToEventMapping[1](player_id) + AIActionToEventMapping[3](player_id) + AIActionToEventMapping[0](player_id),
    lambda player_id: AIActionToEventMapping[1](player_id) + AIActionToEventMapping[4](player_id) + AIActionToEventMapping[0](player_id),
    lambda player_id: AIActionToEventMapping[2](player_id) + AIActionToEventMapping[3](player_id) + AIActionToEventMapping[0](player_id),
    lambda player_id: AIActionToEventMapping[2](player_id) + AIActionToEventMapping[4](player_id) + AIActionToEventMapping[0](player_id),

    lambda player_id: []

]

class ActionIndex(Enum):
    Shoot = 0
    MoveLeft = 1
    MoveRight = 2
    MoveUp = 3
    MoveDown = 4
    MoveLeftUp = 5
    MoveLeftDown = 6
    MoveRightUp = 7
    MoveRightDown = 8
    MoveLeftShoot = 9
    MoveRightShoot = 10
    MoveUpShoot = 11
    MoveDownShoot = 12
    MoveLeftUpShoot = 13
    MoveLeftDownShoot = 14
    MoveRightUpShoot = 15
    MoveRightDownShoot = 16
    StandStill = 17
#
# MoveLeft = enum.auto()
# MoveRight = enum.auto()
# MoveUp = enum.auto()
# MoveDown = enum.auto()
# MoveLeftUp = enum.auto()
# MoveLeftDown = enum.auto()
# MoveRightUp = enum.auto()
# MoveRightDown = enum.auto()
# MoveLeftShoot = enum.auto()
# MoveRightShoot = enum.auto()
# MoveUpShoot = enum.auto()
# MoveDownShoot = enum.auto()
# MoveLeftUpShoot = enum.auto()
# MoveLeftDownShoot = enum.auto()
# MoveRightUpShoot = enum.auto()
# MoveRightDownShoot = enum.auto()
# Shoot = enum.auto()
# StandStill = enum.auto()
