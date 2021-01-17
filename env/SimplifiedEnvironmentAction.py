import enum
from env.EnvironmentAction import EnvironmentAction


class SimplifiedEnvironmentAction(enum.IntEnum):
    Shoot = EnvironmentAction.Shoot
    MoveLeft = EnvironmentAction.MoveLeft
    MoveRight = EnvironmentAction.MoveRight
    MoveUp = EnvironmentAction.MoveUp
    MoveDown = EnvironmentAction.MoveDown
