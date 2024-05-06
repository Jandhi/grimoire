from enum import Enum

from glm import ivec3

from grimoire.core.noise.rng import RNG
from grimoire.core.utils.easings import ease_in_out_cubic, ease_in_out_quint


class DitheringPattern(Enum):
    none = "none"
    random = "random"
    random_ease_cubic = "random_ease_cubic"
    random_ease_quint = "random_ease_quint"
    regular = "regular"

    def calculate_index(
        self,
        value: float,
        dimension_range: int,
        position: ivec3,
        rng: RNG,
    ):
        if self == DitheringPattern.none:
            step_size = 1.0 / dimension_range
            return int(value / step_size)

        if self == DitheringPattern.regular:
            return calculate_dither_regular(value, dimension_range, position)

        if self == DitheringPattern.random:
            return calculate_dither_random(value, dimension_range, rng)

        if self == DitheringPattern.random_ease_cubic:
            return calculate_dither_random(
                value, dimension_range, rng, ease_in_out_cubic
            )

        if self == DitheringPattern.random_ease_quint:
            return calculate_dither_random(
                value, dimension_range, rng, ease_in_out_quint
            )


def calculate_dither_regular(value: float, range: int, position: ivec3) -> int:
    step_size = 1.0 / (range - 1)  # each step is a range from A to B
    index = int(value / step_size)
    remainder = (value / step_size) - index

    # upper
    if remainder > 3 / 4:
        return index + 1

    # half dither
    if remainder > 1 / 4:
        if sum(position) % 2 == 0:
            return index + 1
        return index

    return index


def calculate_dither_random(value: float, range: int, rng: RNG, easing=None) -> int:
    step_size = 1.0 / (range - 1)  # each step is a range from A to B

    if easing is None:

        def easing(x):
            return x

    index = int(value / step_size)
    remainder = easing((value / step_size) - index)
    percent_chance = int(remainder * 100)

    if rng.percent(percent_chance):
        return index + 1
    else:
        return index
