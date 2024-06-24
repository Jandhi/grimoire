# Allows code to be run in root directory
import sys

sys.path[0] = sys.path[0].removesuffix("\\tests\\path")

from glm import ivec2
from grimoire.core.assets.asset_loader import load_assets
from grimoire.core.generator.test import TestModule
from grimoire.core.noise.rng import RNG
from grimoire.core.styling.palette import Palette
from grimoire.paths.bridge import BridgeBuilder
from grimoire.story.load_story_types import load_types


# Actual file
from gdpc import Editor, Block
from gdpc.vector_tools import ivec3, length
from grimoire.paths.route_highway import route_highway, fill_out_highway
from grimoire.paths.build_highway import build_highway
from grimoire.core.maps import Map


class TestBridge(TestModule):
    def test(self):
        load_types()
        load_assets("grimoire/asset_data", parent_module=self)

        SEED = 36322

        editor = Editor(buffering=True, bufferLimit=5, caching=True)

        area = editor.getBuildArea()
        editor.transform = (area.begin.x, 0, area.begin.z)

        print("Loading world slice...")
        build_rect = area.toRect()
        world_slice = editor.loadWorldSlice(build_rect)
        print("World slice loaded!")

        build_map = Map(world_slice)

        start = build_map.make_3d(ivec2(0, 0))
        end = build_map.make_3d(ivec2(build_map.width - 1, (build_map.depth - 1) - 3))

        rng = RNG(SEED)
        palette = Palette.find("medieval")

        bridge_length = length(end - start)

        BridgeBuilder(
            self, editor, palette, start, end, int(bridge_length**0.5 / 2), 4
        ).run()

        editor.placeBlock(start, Block("red_wool"))
        editor.placeBlock(end, Block("blue_wool"))


if __name__ == "__main__":
    TestBridge().run()
