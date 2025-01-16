from typing import TypeVar

from glm import ivec2, ivec3

from .random import *

T = TypeVar("T")


# Class that wraps the seed value
class Seed:
    def __init__(self, value) -> None:
        self._value = value

    def value(self) -> int:
        return self._value

    # random.py functions
    def randint(self, max: int) -> int:
        return randint(self.value(), max)

    def randpoint_2d(self, max: ivec2) -> ivec2:
        return ivec2(self.randint(max.x), self.randint(max.y))

    def randpoint_3d(self, max: ivec3) -> ivec3:
        return ivec3(self.randint(max.x), self.randint(max.y), self.randint(max.z))

    def randrange(self, min: int, max: int) -> int:
        return randrange(self.value(), min, max)

    def randpoint_2d_range(self, min: ivec2, max: ivec2) -> ivec2:
        return ivec2(self.randrange(min.x, max.x), self.randrange(min.y, max.y))

    def randpoint_3d_range(self, min: ivec3, max: ivec3) -> ivec3:
        return ivec3(self.randrange(min.x, max.x), self.randrange(min.y, max.y), self.randrange(min.z, max.z))

    def choose(self, items: list[T]) -> T:
        return choose(self.value(), items)

    def pop(self, items: list[T]) -> T:
        return pop(self.value(), items)

    def choose_weighted(self, items: dict[T, int]) -> T:
        return choose_weighted(self.value(), items)

    def pop_weighted(self, items: dict[T, int]) -> T:
        return pop_weighted(self.value(), items)

    def odds(self, successes: int, failures: int) -> bool:
        return odds(self.value(), successes, failures)

    def chance(self, successes: int, total: int) -> bool:
        return chance(self.value(), successes, total)

    def percent(self, successes: int) -> bool:
        return self.chance(successes, 100)

    def shuffle(self, items: list) -> list:
        return shuffle(self.value(), items)
