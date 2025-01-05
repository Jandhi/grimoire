# Allows code to be run in root directory
import sys

from grimoire.core.styling.materials.painter import Painter
from grimoire.core.styling.materials.traversal import MaterialTraversalStrategy

sys.path[0] = sys.path[0].removesuffix("tests\\materials")

# Start of real file

from glm import ivec3

from grimoire.core.styling.blockform import BlockForm
from grimoire.core.generator.test import run_test, EditingTestModule
from grimoire.core.logger import LoggerSettings, LoggingLevel
from grimoire.core.styling.materials.gradient import (
    Gradient,
    GradientAxis,
    PerlinSettings,
)
from grimoire.core.noise.global_seed import GlobalSeed

from grimoire.core.styling.materials.material import (
    Material,
    MaterialFeature,
)
from grimoire.core.assets.asset_loader import load_assets


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

        material: Material = Material.get("bricks1")
        gradient = Gradient(
            13, self.build_map, 1.0, PerlinSettings(20, 8, 2)
        ).with_axis(GradientAxis.x(0, self.build_rect.size.x - 1))
        painter = Painter(self.editor, material).with_feature(
            MaterialFeature.MOISTURE,
            gradient.to_func(),
            MaterialTraversalStrategy.SCALED,
        )

        for x in self.log.progress(range(self.build_rect.size.x), "Building rows"):
            for z in range(self.build_rect.size.y):
                painter.place_block(ivec3(x, 4, z))
