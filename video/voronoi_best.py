# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\video')

from districts.tests.draw_districts import draw_districts
from districts.tests.place_colors import get_color_differentiated, place_relative_to_ground
from structures.directions import cardinal, vector
from terrain.logger import log_trees
from districts.generate_districts import spawn_districts, get_neighbours, bubble_out, generate_districts
from maps.build_map import get_build_map
from maps.water_map import get_water_map

from gdpc import Editor, Block, WorldSlice
from gdpc.vector_tools import ivec2, ivec3
from districts.district import District

editor = Editor(buffering=True, caching=True)
area = editor.getBuildArea()
print(area)
editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

log_trees(editor, build_rect, world_slice)

print("Reload post logging slice!")
world_slice = editor.loadWorldSlice(build_rect)

seed = 13


water_map = get_water_map(world_slice)
build_map = get_build_map(world_slice)

districts, district_map = generate_districts(seed, build_rect, world_slice, water_map)

for district in districts:
    for point in district.points:
        x, z = point.x, point.z

        block = get_color_differentiated(district, districts, water_map[x][z])

        y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z]
        place_relative_to_ground(x, 0, z, block, world_slice, editor)
