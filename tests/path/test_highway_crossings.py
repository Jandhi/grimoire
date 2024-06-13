# Allows code to be run in root directory
import sys

from glm import ivec2

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

map = Map(world_slice)

bottom_left = map.make_3d(ivec2(0, 0))
top_right = map.make_3d(
    ivec2(
        (world_slice.box.size.x - 1) - (world_slice.box.size.x - 1) % 4,
        (world_slice.box.size.z - 1) - (world_slice.box.size.z - 1) % 4,
    )
)
bottom_right = map.make_3d(
    ivec2((world_slice.box.size.x - 1) - (world_slice.box.size.x - 1) % 4, 0)
)
top_left = map.make_3d(
    ivec2(0, (world_slice.box.size.z - 1) - (world_slice.box.size.z - 1) % 4)
)

editor.placeBlock(bottom_left, Block("minecraft:glowstone"))
editor.placeBlock(top_right, Block("minecraft:glowstone"))


def route(start, end):
    highway = route_highway(start, end, map, editor, is_debug=True)
    highway = fill_out_highway(highway)
    build_highway(highway, editor, world_slice, map)


route(bottom_left, top_right)
route(bottom_left + ivec3(0, 0, 20), top_right)
