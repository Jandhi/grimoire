# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\paths\\tests')

# Actual file
from gdpc import Editor, Block
from gdpc.vector_tools import ivec2, ivec3
from paths.highway import route_highway, find_highway_points
from terrain.water_map import get_water_map
from terrain.set_height import set_height
from structures.directions import cardinal, get_ivec3, up
from utils.bounds import is_in_bounds

SEED = 36322

editor = Editor(buffering=True, bufferLimit=5, caching=True)

area = editor.getBuildArea()
editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

water_map = get_water_map(world_slice)

start_x, start_z = 0, 0
start_y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][start_x][start_z]
start = ivec3(start_x, start_y, start_z)

end_x, end_z = world_slice.box.size.x - 1, world_slice.box.size.z - 1
end_x = end_x - end_x % 4
end_z = end_z - end_z % 4
end_y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][end_x][end_z]
end = ivec3(end_x, end_y, end_z)

editor.placeBlock(start, Block('minecraft:glowstone'))
editor.placeBlock(end, Block('minecraft:glowstone'))

highway = route_highway(start, end, world_slice, water_map, editor)
highway = find_highway_points(highway)

for point in highway:
    editor.placeBlock(point - get_ivec3(up), Block('red_wool'))
    editor.placeBlock(point, Block('air'))
    editor.placeBlock(point + get_ivec3(up), Block('air'))
    editor.placeBlock(point + get_ivec3(up) * 2, Block('air'))

    for direction in cardinal:
        neighbour = point + get_ivec3(direction)

        if not is_in_bounds(neighbour, world_slice):
            continue

        editor.placeBlock(neighbour - get_ivec3(up), Block('cobblestone'))
        editor.placeBlock(neighbour, Block('air'))
        editor.placeBlock(neighbour + get_ivec3(up), Block('air'))
        editor.placeBlock(neighbour + get_ivec3(up) * 2, Block('air'))

