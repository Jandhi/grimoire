# Allows code to be run in root directory
import sys

from grimoire.core.structures.directions import Directions2D
from grimoire.core.utils.bounds import is_in_bounds, is_in_bounds2d
from grimoire.core.utils.easings import ease_out_quad

sys.path[0] = sys.path[0].removesuffix("tests\\materials")

# Start of real file

from gdpc import Editor
from glm import ivec3, ivec2

from grimoire.core.generator.test import TestModule, run_test, EditingTestModule
from grimoire.core.logger import LoggerSettings, LoggingLevel
from grimoire.core.materials.dithering import DitheringPattern
from grimoire.core.materials.gradient import Gradient, GradientAxis, PerlinSettings
from grimoire.core.noise.global_seed import GlobalSeed
from grimoire.core.noise.perlin.perlin_noise import PerlinNoise
from grimoire.core.noise.rng import RNG
from grimoire.core.utils.misc import average

from grimoire.core.materials.material import Material, BasicMaterial, MaterialParameters
from grimoire.buildings.walls.wall import Wall
from grimoire.core.assets.load_assets import load_assets


@run_test
class MaterialPathTest(EditingTestModule):
    catch_errors = False

    def test(self):
        GlobalSeed.set(173)

        self.init_rng_from_world_seed()
        load_assets(
            "grimoire\\asset_data",
            LoggerSettings(minimum_console_level=LoggingLevel.ERROR),
        )
        self.load_world()

        material: BasicMaterial = Material.find("cobblestone")
        gradient = Gradient(254, perlin_settings=PerlinSettings(23, 6, 1.6, 0.3))
        material.dithering_pattern = DitheringPattern.random_ease_cubic

        path = []
        for i in range(5, min(self.build_rect.size.x, self.build_rect.size.y) - 5):
            path.append(ivec2(i, i))

        points = [(point, 0) for point in path]
        visited = set(path)
        max_dist = 10
        queue = points.copy()

        while len(queue) > 0:
            (point, dist) = queue.pop(0)

            if dist == max_dist:
                continue

            for d in Directions2D.Cardinal:
                neighbour = point + d

                if neighbour in visited:
                    continue

                points.append((neighbour, dist + 1))
                queue.append((neighbour, dist + 1))
                visited.add(neighbour)

        for point, dist in points:
            if not is_in_bounds2d(point, self.world_slice):
                continue

            x, z = point
            y = self.world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][x, z] - 1
            pos = ivec3(x, y, z)

            build_val = gradient.calculate_shade(pos, 1 - dist / max_dist)

            if build_val < 0.5:
                continue

            material.place_block(
                self.editor,
                MaterialParameters(
                    position=pos,
                    age=0,
                    shade=gradient.calculate_shade(pos, 1 - dist / max_dist),
                    moisture=0,
                ),
                self.rng,
            )
