# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\districts\\tests')

# Actual file
from gdpc import Editor, Block
from gdpc.vector_tools import ivec2, ivec3
from districts.generate_districts import generate_districts
from districts.tests.place_colors import get_color_differentiated, place_relative_to_ground
from terrain.water_map import get_water_map
from districts.tests.draw_districts import draw_districts

SEED = 36322

editor = Editor(buffering=True, caching=True)

area = editor.getBuildArea()
editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

player_pos = ivec2(area.size.x // 2, area.size.z // 2)

water_map = get_water_map(world_slice)
districts, district_map = generate_districts(SEED, build_rect, world_slice, water_map)



draw_districts(build_rect, district_map, water_map, world_slice, editor)

for district in districts:
    x = district.origin.x
    z = district.origin.z

    y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z] + 10
    editor.placeBlock((x, y, z), Block('sea_lantern'))