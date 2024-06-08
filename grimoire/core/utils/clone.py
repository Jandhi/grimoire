from typing import TypeVar

from glm import ivec3, ivec2

T = TypeVar("T")


def clone(item: T) -> T:
    if isinstance(item, list):
        return list(item)
    if isinstance(item, dict):
        return dict(item)
    if isinstance(item, ivec2):
        pass
    if isinstance(item, ivec3):
        return ivec3(*item)

    clone_func = getattr(item, "clone", None)
    if callable(clone_func):
        return clone_func(item)

    return item
