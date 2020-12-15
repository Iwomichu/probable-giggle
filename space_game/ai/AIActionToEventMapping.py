from typing import List, Callable, Dict

from space_game.events.PlayerAcceleratedEvent import PlayerAcceleratedEvent
from space_game.events.PlayerShootsEvent import PlayerShootsEvent
from space_game.AccelerationDirection import AccelerationDirection
from space_game.ai.AIAction import AIAction
from space_game.events.Event import Event
from space_game.domain_names import PlayerId


AIActionToEventMapping: Dict[AIAction, Callable[[PlayerId], List[Event]]] = {
    AIAction.StandStill: lambda player_id: [],

    AIAction.MoveLeft: lambda player_id: [PlayerAcceleratedEvent(player_id, AccelerationDirection.LEFT)],
    AIAction.MoveRight: lambda player_id: [PlayerAcceleratedEvent(player_id, AccelerationDirection.RIGHT)],
    AIAction.MoveUp: lambda player_id: [PlayerAcceleratedEvent(player_id, AccelerationDirection.UP)],
    AIAction.MoveDown: lambda player_id: [PlayerAcceleratedEvent(player_id, AccelerationDirection.DOWN)],

    AIAction.MoveLeftUp: lambda player_id: AIActionToEventMapping[AIAction.MoveLeft](player_id) + AIActionToEventMapping[AIAction.MoveUp](player_id),
    AIAction.MoveLeftDown: lambda player_id: AIActionToEventMapping[AIAction.MoveLeft](player_id) + AIActionToEventMapping[AIAction.MoveDown](player_id),
    AIAction.MoveRightUp: lambda player_id: AIActionToEventMapping[AIAction.MoveRight](player_id) + AIActionToEventMapping[AIAction.MoveUp](player_id),
    AIAction.MoveRightDown: lambda player_id: AIActionToEventMapping[AIAction.MoveRight](player_id) + AIActionToEventMapping[AIAction.MoveDown](player_id),

    AIAction.Shoot: lambda player_id: [PlayerShootsEvent(player_id)],

    AIAction.MoveLeftShoot: lambda player_id: AIActionToEventMapping[AIAction.MoveLeft](player_id) + AIActionToEventMapping[AIAction.Shoot](player_id),
    AIAction.MoveRightShoot: lambda player_id: AIActionToEventMapping[AIAction.MoveRight](player_id) + AIActionToEventMapping[AIAction.Shoot](player_id),
    AIAction.MoveUpShoot: lambda player_id: AIActionToEventMapping[AIAction.MoveUp](player_id) + AIActionToEventMapping[AIAction.Shoot](player_id),
    AIAction.MoveDownShoot: lambda player_id: AIActionToEventMapping[AIAction.MoveDown](player_id) + AIActionToEventMapping[AIAction.Shoot](player_id),
    AIAction.MoveLeftUpShoot: lambda player_id: AIActionToEventMapping[AIAction.MoveLeftUp](player_id) + AIActionToEventMapping[AIAction.Shoot](player_id),
    AIAction.MoveLeftDownShoot: lambda player_id: AIActionToEventMapping[AIAction.MoveLeftDown](player_id) + AIActionToEventMapping[AIAction.Shoot](player_id),
    AIAction.MoveRightUpShoot: lambda player_id: AIActionToEventMapping[AIAction.MoveRightUp](player_id) + AIActionToEventMapping[AIAction.Shoot](player_id),
    AIAction.MoveRightDownShoot: lambda player_id: AIActionToEventMapping[AIAction.MoveRightDown](player_id) + AIActionToEventMapping[AIAction.Shoot](player_id),


}
# StandStill = auto()
#
# MoveLeft = auto()
# MoveRight = auto()
# MoveUp = auto()
# MoveDown = auto()
#
# MoveLeftUp = auto()
# MoveLeftDown = auto()
# MoveRightUp = auto()
# MoveRightDown = auto()
#
# Shoot = auto()
#
# MoveLeftShoot = auto()
# MoveRightShoot = auto()
# MoveUpShoot = auto()
# MoveDownShoot = auto()
#
# MoveLeftUpShoot = auto()
# MoveLeftDownShoot = auto()
# MoveRightUpShoot = auto()
# MoveRightDownShoot = auto()
