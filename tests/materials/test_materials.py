# Allows code to be run in root directory
import sys

sys.path[0] = sys.path[0].removesuffix("tests\\materials")

# Start of real file

from gdpc import Editor
from glm import ivec3

from grimoire.core.generator.test import TestModule, run_test, EditingTestModule
from grimoire.core.logger import LoggerSettings, LoggingLevel
from grimoire.core.materials.dithering import DitheringPattern
from grimoire.core.materials.gradient import Gradient, GradientAxis
from grimoire.core.noise.global_seed import GlobalSeed
from grimoire.core.noise.perlin.perlin_noise import PerlinNoise
from grimoire.core.noise.rng import RNG
from grimoire.core.utils.misc import average

from grimoire.core.materials.material import Material, BasicMaterial, MaterialParameters
from grimoire.buildings.walls.wall import Wall
from grimoire.core.assets.load_assets import load_assets


@run_test
class MaterialsTest(EditingTestModule):
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
        gradient = Gradient(13).with_axis(GradientAxis.x(0, self.build_rect.size.x - 1))
        material.dithering_pattern = DitheringPattern.random_ease_cubic

        for x in range(self.build_rect.size.x):
            for z in range(self.build_rect.size.y):

                material.place_block(
                    self.editor,
                    MaterialParameters(
                        position=ivec3(x, 4, z),
                        shade=gradient.calculate_shade(
                            ivec3(x, 4, z),
                        ),
                        age=0,
                        moisture=0,
                    ),
                    self.rng,
                )
