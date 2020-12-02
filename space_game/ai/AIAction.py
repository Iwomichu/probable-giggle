from enum import IntEnum, auto


class AIAction(IntEnum):
    StandStill = 0

    MoveLeft = 1
    MoveRight = 2
    MoveUp = 4
    MoveDown = 8

    MoveLeftUp = MoveLeft + MoveUp
    MoveLeftDown = MoveLeft + MoveDown
    MoveRightUp = MoveRight + MoveUp
    MoveRightDown = MoveRight + MoveDown

    Shoot = 16

    MoveLeftShoot = MoveLeft + Shoot
    MoveRightShoot = MoveRight + Shoot
    MoveUpShoot = MoveUp + Shoot
    MoveDownShoot = MoveDown + Shoot

    MoveLeftUpShoot = MoveLeftUp + Shoot
    MoveLeftDownShoot = MoveLeftDown + Shoot
    MoveRightUpShoot = MoveRightUp + Shoot
    MoveRightDownShoot = MoveRightDown + Shoot
