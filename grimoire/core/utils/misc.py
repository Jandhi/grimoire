# For generally random helpful functions
import math
from numbers import Number
from time import sleep
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


def growth_spurt(editor: Editor):
    editor.runCommand("time set day")
    editor.runCommand("gamerule randomTickSpeed 5000")
    sleep(0.5)  # 500 ms = 10 game ticks
    editor.runCommand("gamerule randomTickSpeed 3")


def kill_items(editor: Editor):
    return editor.runCommand("kill @e[type=minecraft:item]")
