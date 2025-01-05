import abc
import dataclasses
from typing import Callable

from gdpc.vector_tools import DIRECTIONS_3D, Rect
from glm import ivec3, vec3
from perlin_noise import PerlinNoise

from grimoire.core.maps import Map
from grimoire.core.structures.axis import Axes, Axis
from grimoire.core.utils.bounds import clamp
from grimoire.core.utils.misc import average, lerp


@dataclasses.dataclass
class PerlinSettings:
    base_octaves: float
    noise_layers: int
    # The ratio of how fast the higher perlin octaves fall off
    add_ratio: float


@dataclasses.dataclass
class GradientAxis:
    axis: Axis
    min_val: int
    max_val: int
    is_reversed: bool

    def find_gradient_value(self, pos: ivec3) -> float:
        if self.max_val == self.min_val:
            return 0.5

        base_val = self.axis.get(pos)
        grad_val = (base_val - self.min_val) / (self.max_val - self.min_val)
        if self.is_reversed:
            return 1.0 - clamp(grad_val, 0.0, 1.0)
        else:
            return clamp(grad_val, 0.0, 1.0)

    @staticmethod
    def x(min_val, max_val, is_reversed=False) -> "GradientAxis":
        return GradientAxis(Axes.X, min_val, max_val, is_reversed)

    @staticmethod
    def y(min_val, max_val, is_reversed=False) -> "GradientAxis":
        return GradientAxis(Axes.Y, min_val, max_val, is_reversed)

    @staticmethod
    def z(min_val, max_val, is_reversed=False) -> "GradientAxis":
        return GradientAxis(Axes.Z, min_val, max_val, is_reversed)


class Gradient:
    default_perlin_settings = PerlinSettings(
        base_octaves=27, noise_layers=6, add_ratio=1.7
    )

    def __init__(
        self,
        seed,
        build_map: Map,
        noise_strength: float = 0.3,  # The amount that the perlin is reflected with in the final result
        noise_settings: PerlinSettings = None,
    ):
        self.axes = []
        self.map = build_map
        self.noise_strength = noise_strength

        if noise_settings is None:
            noise_settings = Gradient.default_perlin_settings

        self.perlin_settings = noise_settings

        self.noises = [
            PerlinNoise(octaves=self.perlin_settings.base_octaves * 2**i, seed=seed)
            for i in range(self.perlin_settings.noise_layers)
        ]

    # Builder pattern to add axes to the gradient
    def with_axis(self, axis: GradientAxis) -> "Gradient":
        self.axes.append(axis)
        return self

    # Calculates the gradient value without perlin noise
    def calculate_gradient_value(self, pos: ivec3) -> float:
        if len(self.axes) == 0:
            return 0.5

        return average([axis.find_gradient_value(pos) for axis in self.axes])

    # We average the value across its orthogonal neighbours
    def calculate_value(self, pos: ivec3, grad_val: float = None):
        return average(
            [
                self.calculate_point_value(pos + d, grad_val)
                for d in {ivec3(0, 0, 0)} | DIRECTIONS_3D
            ]
        )

    # Make a vec appear between 0 and 1
    def normalize_vec(self, vec: ivec3) -> vec3:
        return vec3(
            float(vec.x) / self.map.world.rect.size.x,
            float(vec.y) / self.map.world.ySize,
            float(vec.z) / self.map.world.rect.size.y,
        )

    def calculate_point_value(self, pos: ivec3, grad_val: float = None):
        perlin_val = 0.5 + sum(
            self.noises[i](list(self.normalize_vec(pos)))
            / (self.perlin_settings.add_ratio**i)
            for i in range(self.perlin_settings.noise_layers)
        )

        grad_val = (
            grad_val if grad_val is not None else self.calculate_gradient_value(pos)
        )

        return clamp(
            lerp(grad_val, perlin_val, self.noise_strength),
            0.0,
            1.0,
        )

    def to_func(self) -> Callable[[ivec3], float]:
        def func(pos: ivec3):
            return self.calculate_point_value(pos)

        return func
