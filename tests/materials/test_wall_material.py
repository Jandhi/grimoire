import sys
from pathlib import Path

from grimoire.core.styling.blockform import BlockForm

sys.path[0] = sys.path[0].removesuffix(str(Path("tests/materials")))
print(f"PATH: {sys.path[0]}")

from glm import ivec2, ivec3

from grimoire.core.assets.asset_loader import load_assets
from grimoire.core.generator.test import EditingTestModule, run_test
from grimoire.core.logger import LoggerSettings, LoggingLevel
from grimoire.core.maps import Map
from grimoire.core.noise.global_seed import GlobalSeed
from grimoire.core.styling.materials.gradient import (
    Gradient,
    PerlinSettings,
    GradientAxis,
)
from grimoire.core.styling.materials.material import MaterialFeature
from grimoire.core.styling.materials.painter import PalettePainter
from grimoire.core.styling.materials.traversal import MaterialTraversalStrategy
from grimoire.core.styling.palette import Palette, MaterialRole


@run_test
class WallMaterialTest(EditingTestModule):
    catch_errors = False

    def test(self):
        GlobalSeed.set(173)

        self.init_rng_from_world_seed()
        load_assets(
            "grimoire/asset_data",
            LoggerSettings(minimum_console_level=LoggingLevel.INFO),
        )
        self.load_world()

        palette = Palette.get("medieval")
        build_map = Map(self.world_slice)

        painter = (
            PalettePainter(self.editor, palette)
            .with_feature(
                MaterialFeature.SHADE,
                Gradient(0, build_map, noise_settings=PerlinSettings(8, 6, 2))
                .with_axis(GradientAxis.y(build_map.height_at(ivec2(0, 0)), 20))
                .to_func(),
                MaterialTraversalStrategy.SCALED,
            )
            .with_feature(
                MaterialFeature.MOISTURE,
                Gradient(
                    0, build_map, 1.0, noise_settings=PerlinSettings(8, 6, 2)
                ).to_func(),
                MaterialTraversalStrategy.SCALED,
            )
        )

        for xz in range(20):
            y = build_map.height_at(ivec2(xz, xz))
            for dy in range(20):
                painter.place_block(ivec3(xz, y + dy, xz), MaterialRole.PRIMARY_STONE)
