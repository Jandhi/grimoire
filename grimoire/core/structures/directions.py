from enum import Enum

from glm import ivec3, ivec2


# NOTE: Unused class; replace with GDPC vectors
class Directions2D:
    Zero = ivec2(0, 0)

    XPlus = ivec2(1, 0)
    XMinus = ivec2(-1, 0)
    ZPlus = ivec2(0, 1)
    ZMinus = ivec2(0, -1)

    East = XPlus
    West = XMinus
    South = ZPlus
    North = ZMinus

    Northeast = North + East
    Northwest = North + West
    Southeast = South + East
    Southwest = South + West

    Cardinal = [North, East, South, West]
    Diagonals = [Northeast, Northwest, Southeast, Southwest]
    All8 = Cardinal + Diagonals


class Directions:
    Zero = ivec3(0, 0, 0)

    XPlus = ivec3(1, 0, 0)
    XMinus = ivec3(-1, 0, 0)
    YPlus = ivec3(0, 1, 0)
    YMinus = ivec3(0, -1, 0)
    ZPlus = ivec3(0, 0, 1)
    ZMinus = ivec3(0, 0, -1)

    East = XPlus
    West = XMinus
    Up = YPlus
    Down = YMinus
    South = ZPlus
    North = ZMinus

    Northeast = North + East
    Northwest = North + West
    Southeast = South + East
    Southwest = South + West

    Cardinal = [North, East, South, West]
    Diagonals = [Northeast, Northwest, Southeast, Southwest]
    Orthogonal = Cardinal + [Up, Down]
    All8 = Cardinal + Diagonals
    Omni = [ivec3(*(i % 3 - 1, (i // 3) % 3 - 1, i // 9 - 1)) for i in range(1, 27)]


class Axis:
    def __init__(self, name: str, index: int):
        self.name = name
        self.index = index

    def get(self, vec: ivec3) -> int:
        return vec[self.index]


class Axes:
    X = Axis("x", 0)
    Y = Axis("y", 1)
    Z = Axis("z", 2)
