from glm import ivec3

from grimoire.core.noise.perlin.perlin_noise import PerlinNoise
from grimoire.core.structures.directions import Directions, Direction
from grimoire.core.utils.misc import average


class Gradient:
    def __init__(
        self,
        seed,
        base_octaves=50,
        noise_layers=6,
        add_ratio=1.7,
        perlin_strength=1 / 3,
    ):
        self.noises = [
            PerlinNoise(octaves=base_octaves * 2**i, seed=seed)
            for i in range(noise_layers)
        ]
        self.noise_layers = noise_layers
        self.add_ratio = add_ratio
        self.perlin_strength = perlin_strength

    # We average shading across its orthogonal neighbours
    def calculate_shade(self, pos: ivec3, gradient_val: float):
        shade_val = average(
            self.calculate_point_shade(pos + d, gradient_val)
            for d in [Directions.Zero] + Directions.Orthogonal
        )

        return shade_val

    def calculate_point_shade(self, pos: ivec3, gradient_val: float):
        perlin_val = sum(
            self.noises[i](list(pos)) / (self.add_ratio**i)
            for i in range(self.noise_layers)
        )

        shade_val = max(
            0.0, min(1.0, gradient_val + (perlin_val * self.perlin_strength))
        )

        return shade_val
