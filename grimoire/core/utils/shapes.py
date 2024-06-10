from dataclasses import dataclass
from typing import AbstractSet, Iterable, Iterator

from gdpc.vector_tools import ivec2, ivec3, Rect, Box


@dataclass
class Shape2D(set):
    """
    A custom set class representing a 2D shape with updated bounds based on the elements it contains.

    Explanation:
    This class extends the set class to represent a 2D shape with updated bounds (begin and end) that automatically adjust when elements are added or removed.

    Args:
        element: The 2D vector element to be added to the shape.

    Raises:
        NotImplementedError: This method is not implemented in the base class.
    """

    begin: ivec2
    end: ivec2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recalculate_bounds()

    def recalculate_bounds(self) -> None:
        if len(self) > 0:
            x_values, y_values = zip(*self)
            self.begin = ivec2(min(x_values), min(y_values))
            self.end = ivec2(max(x_values), max(y_values))
        else:
            self.begin = ivec2(0, 0)
            self.end = ivec2(0, 0)

    def update_bounds(self, element: ivec2) -> None:
        if element.x < self.begin.x:
            self.begin.x = element.x
        elif element.x > self.end.x:
            self.end.x = element.x

        if element.y < self.begin.y:
            self.begin.y = element.y
        elif element.y > self.end.y:
            self.end.y = element.y

    def add(self, element: ivec2, /) -> None:
        super().add(element)
        self.update_bounds(element)

    def difference(self, *s: Iterable[ivec2]):
        raise NotImplementedError()

    def difference_update(self, *s: Iterable[ivec2]) -> None:
        raise NotImplementedError()

    def discard(self, element: ivec2, /) -> None:
        raise NotImplementedError()

    def intersection(self, *s: Iterable[ivec2]):
        raise NotImplementedError()

    def intersection_update(self, *s: Iterable[ivec2]) -> None:
        raise NotImplementedError()

    def isdisjoint(self, s: Iterable[ivec2], /) -> bool:
        raise NotImplementedError

    def issubset(self, s: Iterable[ivec2], /) -> bool:
        raise NotImplementedError()

    def issuperset(self, s: Iterable[ivec2], /) -> bool:
        raise NotImplementedError()

    def remove(self, element: ivec2, /) -> None:
        raise NotImplementedError()

    def symmetric_difference(self, s: Iterable[ivec2], /):
        raise NotImplementedError()

    def symmetric_difference_update(self, s: Iterable[ivec2], /) -> None:
        raise NotImplementedError()

    def union(self, *s: Iterable[ivec2]) -> set[ivec2]:
        raise NotImplementedError()

    def update(self, *s: Iterable[ivec2]) -> None:
        raise NotImplementedError()

    def __and__(self, value: AbstractSet[object], /):
        raise NotImplementedError()

    def __iand__(self, value: AbstractSet[object], /):
        raise NotImplementedError()

    def __or__(self, value: AbstractSet[ivec2], /):
        raise NotImplementedError()

    def __ior__(self, value: AbstractSet[ivec2], /):
        raise NotImplementedError()

    def __sub__(self, value: AbstractSet[ivec2 | None], /):
        raise NotImplementedError()

    def __isub__(self, value: AbstractSet[object], /):
        raise NotImplementedError()

    def __xor__(self, value: AbstractSet[ivec2], /):
        raise NotImplementedError()

    def __ixor__(self, value: AbstractSet[ivec2], /):
        raise NotImplementedError()

    def __le__(self, value: AbstractSet[object], /) -> bool:
        raise NotImplementedError()

    def __lt__(self, value: AbstractSet[object], /) -> bool:
        raise NotImplementedError()

    def __ge__(self, value: AbstractSet[object], /) -> bool:
        raise NotImplementedError()

    def __gt__(self, value: AbstractSet[object], /) -> bool:
        raise NotImplementedError()

    def __eq__(self, value: object, /) -> bool:
        raise NotImplementedError()

    def to_boundry_rect(self) -> Rect:
        return Rect(self.begin, self.end - self.begin)

    def get_largest_rect(self) -> Rect:
        raise NotImplementedError()


@dataclass
class Shape3D(set):
    """
    A custom set class representing a 3D shape with updated bounds based on the elements it contains.

    Explanation:
    This class extends the set class to represent a 3D shape with updated bounds (begin and end) that automatically adjust when elements are added or removed.

    Args:
        element: The 3D vector element to be added to the shape.

    Raises:
        NotImplementedError: This method is not implemented in the base class.
    """

    begin: ivec3
    end: ivec3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recalculate_bounds()

    def recalculate_bounds(self) -> None:
        if len(self) > 0:
            x_values, y_values, z_values = zip(*self)
            self.begin = ivec3(min(x_values), min(y_values), min(z_values))
            self.end = ivec3(max(x_values), max(y_values), max(z_values))
        else:
            self.begin = ivec3(0, 0, 0)
            self.end = ivec3(0, 0, 0)

    def update_bounds(self, element: ivec3) -> None:
        if element.x < self.begin.x:
            self.begin.x = element.x
        elif element.x > self.end.x:
            self.end.x = element.x

        if element.y < self.begin.y:
            self.begin.y = element.y
        elif element.y > self.end.y:
            self.end.y = element.y

        if element.z < self.begin.z:
            self.begin.z = element.z
        elif element.z > self.end.z:
            self.end.z = element.z

    def add(self, element: ivec3, /) -> None:
        super().add(element)
        self.update_bounds(element)

    def difference(self, *s: Iterable[ivec3]):
        raise NotImplementedError()

    def difference_update(self, *s: Iterable[ivec3]) -> None:
        raise NotImplementedError()

    def discard(self, element: ivec3, /) -> None:
        raise NotImplementedError()

    def intersection(self, *s: Iterable[ivec3]):
        raise NotImplementedError()

    def intersection_update(self, *s: Iterable[ivec3]) -> None:
        raise NotImplementedError()

    def isdisjoint(self, s: Iterable[ivec3], /) -> bool:
        raise NotImplementedError

    def issubset(self, s: Iterable[ivec3], /) -> bool:
        raise NotImplementedError()

    def issuperset(self, s: Iterable[ivec3], /) -> bool:
        raise NotImplementedError()

    def remove(self, element: ivec3, /) -> None:
        raise NotImplementedError()

    def symmetric_difference(self, s: Iterable[ivec3], /):
        raise NotImplementedError()

    def symmetric_difference_update(self, s: Iterable[ivec3], /) -> None:
        raise NotImplementedError()

    def union(self, *s: Iterable[ivec3]) -> set[ivec3]:
        raise NotImplementedError()

    def update(self, *s: Iterable[ivec3]) -> None:
        raise NotImplementedError()

    def __and__(self, value: AbstractSet[object], /):
        raise NotImplementedError()

    def __iand__(self, value: AbstractSet[object], /):
        raise NotImplementedError()

    def __or__(self, value: AbstractSet[ivec3], /):
        raise NotImplementedError()

    def __ior__(self, value: AbstractSet[ivec3], /):
        raise NotImplementedError()

    def __sub__(self, value: AbstractSet[ivec3 | None], /):
        raise NotImplementedError()

    def __isub__(self, value: AbstractSet[object], /):
        raise NotImplementedError()

    def __xor__(self, value: AbstractSet[ivec3], /):
        raise NotImplementedError()

    def __ixor__(self, value: AbstractSet[ivec3], /):
        raise NotImplementedError()

    def __le__(self, value: AbstractSet[object], /) -> bool:
        raise NotImplementedError()

    def __lt__(self, value: AbstractSet[object], /) -> bool:
        raise NotImplementedError()

    def __ge__(self, value: AbstractSet[object], /) -> bool:
        raise NotImplementedError()

    def __gt__(self, value: AbstractSet[object], /) -> bool:
        raise NotImplementedError()

    def __eq__(self, value: object, /) -> bool:
        raise NotImplementedError()

    def to_box(self) -> Box:
        return Box(self.begin, self.end - self.begin)

    def get_largest_box(self) -> Box:
        raise NotImplementedError()
