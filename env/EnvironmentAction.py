import enum


class EnvironmentAction(enum.IntEnum):
    Shoot = enum.auto()
    MoveLeft = enum.auto()
    MoveRight = enum.auto()
    MoveUp = enum.auto()
    MoveDown = enum.auto()
    MoveLeftUp = enum.auto()
    MoveLeftDown = enum.auto()
    MoveRightUp = enum.auto()
    MoveRightDown = enum.auto()
    MoveLeftShoot = enum.auto()
    MoveRightShoot = enum.auto()
    MoveUpShoot = enum.auto()
    MoveDownShoot = enum.auto()
    MoveLeftUpShoot = enum.auto()
    MoveLeftDownShoot = enum.auto()
    MoveRightUpShoot = enum.auto()
    MoveRightDownShoot = enum.auto()
    StandStill = enum.auto()
