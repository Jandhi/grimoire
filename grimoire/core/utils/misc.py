# For generally random helpful functions
import math
from numbers import Number
from typing import Any, Collection, Iterable, Sequence, TypeVar

from gdpc import Block, Editor, WorldSlice
from gdpc.lookup import WATERS
from gdpc.vector_tools import Rect, distance, ivec2, ivec3


def is_water(point: ivec3, world_slice: WorldSlice):
    block: Block = world_slice.getBlock((point.x, point.y, point.z))
    return block.id in WATERS | {"minecraft:ice", "minecraft:seagrass"}


T = TypeVar("T")


def average(items: Sequence[Number]) -> float:
    return math.fsum(items) / len(items)


def lerp(a: T, b: T, t: float) -> T:
    """Linear Interpolation between a and b, with t as the interpolation factor"""
    return a * (1.0 - t) + b * t


def to_list_or_none(value: Iterable[T] | T | None) -> list[T] | None:
    if isinstance(value, Iterable):
        value = list(value)
    return [value] if value is not None and not isinstance(value, list) else value
