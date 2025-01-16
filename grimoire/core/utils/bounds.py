from typing import Iterator, TypeVar

from gdpc import WorldSlice
from gdpc.vector_tools import ivec2, ivec3


T = TypeVar("T")


def clamp(value: T, minimum: T, maximum: T) -> T:
    """Clamps a value between a minimum and maximum value"""
    return min(maximum, max(minimum, value))


def is_in_bounds(point: ivec3, world_slice: WorldSlice) -> bool:
    """Checks if a point is within the bounds of a world slice"""
    return (
        0 <= point.x < world_slice.box.size.x and 0 <= point.z < world_slice.box.size.z
    )


def is_in_bounds2d(point: ivec2, world_slice: WorldSlice) -> bool:
    """Checks if a point is within the bounds of a world slice"""
    return (
        0 <= point.x < world_slice.box.size.x and 0 <= point.y < world_slice.box.size.z
    )


def area_2d(size: ivec2) -> Iterator[ivec2]:
    """Iterates over all points in a 2D area"""
    for x in range(size.x):
        for y in range(size.y):
            yield ivec2(x, y)
