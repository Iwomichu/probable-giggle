import enum
from typing import Dict

from space_game.ai.AIAction import AIAction


class EnvironmentAction(enum.IntEnum):
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


EnvironmentActionToAIActionMapping: Dict[EnvironmentAction, AIAction] = {
    EnvironmentAction.Shoot: AIAction.Shoot,
    EnvironmentAction.MoveLeft: AIAction.MoveLeft,
    EnvironmentAction.MoveRight: AIAction.MoveRight,
    EnvironmentAction.MoveUp: AIAction.MoveUp,
    EnvironmentAction.MoveDown: AIAction.MoveDown,
    EnvironmentAction.MoveLeftUp: AIAction.MoveLeftUp,
    EnvironmentAction.MoveLeftDown: AIAction.MoveLeftDown,
    EnvironmentAction.MoveRightUp: AIAction.MoveRightUp,
    EnvironmentAction.MoveRightDown: AIAction.MoveRightDown,
    EnvironmentAction.MoveLeftShoot: AIAction.MoveLeftShoot,
    EnvironmentAction.MoveRightShoot: AIAction.MoveRightShoot,
    EnvironmentAction.MoveUpShoot: AIAction.MoveUpShoot,
    EnvironmentAction.MoveDownShoot: AIAction.MoveDownShoot,
    EnvironmentAction.MoveLeftUpShoot: AIAction.MoveLeftUpShoot,
    EnvironmentAction.MoveLeftDownShoot: AIAction.MoveLeftDownShoot,
    EnvironmentAction.MoveRightUpShoot: AIAction.MoveRightUpShoot,
    EnvironmentAction.MoveRightDownShoot: AIAction.MoveRightDownShoot,
    EnvironmentAction.StandStill: AIAction.StandStill,
}
