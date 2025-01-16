# Allows code to be run in root directory
import sys

from glm import ivec2

from grimoire.core.assets.asset_loader import load_assets
from grimoire.core.logger import LoggerSettings, LoggingLevel
from grimoire.core.noise.rng import RNG
from grimoire.core.styling.palette import Palette, MaterialRole

sys.path[0] = sys.path[0].removesuffix("\\tests\\path")

# Actual file
from gdpc import Editor, Block
from gdpc.vector_tools import ivec3
from grimoire.paths.route_highway import route_highway, fill_out_highway
from grimoire.paths.build_highway import build_highway
from grimoire.core.maps import Map

SEED = 36322

editor = Editor(buffering=True, bufferLimit=5, caching=True)

area = editor.getBuildArea()
editor.transform = (area.begin.x, 0, area.begin.z)
rng = RNG(SEED)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

load_assets(
    "grimoire\\asset_data",
    LoggerSettings(minimum_console_level=LoggingLevel.ERROR),
)

build_map = Map(world_slice)

start = build_map.make_3d(ivec2(0, 0))
end = build_map.make_3d(ivec2(build_map.width - 1, build_map.depth - 1))


palette: Palette = Palette.get("medieval")

highways = []


def make_highway(p1: ivec3, p2: ivec3):
    editor.placeBlock(p1, Block("minecraft:glowstone"))
    editor.placeBlock(p2, Block("minecraft:glowstone"))

    highway = fill_out_highway(route_highway(p1, p2, build_map, editor, is_debug=False))
    build_highway(
        highway,
        editor,
        world_slice,
        build_map,
        palette,
        material_role=MaterialRole.PRIMARY_STONE,
    )


make_highway(start, end)

for _ in range(10):
    p1 = build_map.make_3d(rng.randpoint_2d(build_map.size))
    p2 = build_map.make_3d(rng.randpoint_2d(build_map.size))

    make_highway(p1, p2)
