# Allows code to be run in root directory
import sys

from grimoire.core.assets.asset_loader import load_assets
from grimoire.core.logger import LoggerSettings, LoggingLevel
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

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

load_assets(
    "grimoire\\asset_data",
    LoggerSettings(minimum_console_level=LoggingLevel.ERROR),
)

build_map = Map(world_slice)

start_x, start_z = 0, 0
start_y = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][start_x][start_z]
start = ivec3(start_x, start_y, start_z)

end_x, end_z = world_slice.box.size.x - 1, world_slice.box.size.z - 1
end_x = end_x - end_x % 4
end_z = end_z - end_z % 4
end_y = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][end_x][end_z]
end = ivec3(end_x, end_y, end_z)

editor.placeBlock(start, Block("minecraft:glowstone"))
editor.placeBlock(end, Block("minecraft:glowstone"))

palette: Palette = Palette.get("medieval")

highway = route_highway(start, end, build_map, editor, is_debug=True)
highway = fill_out_highway(highway)
build_highway(
    highway,
    editor,
    world_slice,
    build_map,
    palette,
    material_role=MaterialRole.PRIMARY_STONE,
)
