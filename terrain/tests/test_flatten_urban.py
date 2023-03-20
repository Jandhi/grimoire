# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\terrain\\tests')

# Actual file
from gdpc import Editor, Block
from gdpc.vector_tools import ivec2
from districts.generate_districts import generate_districts
from districts.tests.place_colors import get_color, place_relative_to_ground
from terrain.flatten import flatten

SEED = 36322

editor = Editor(buffering=True, caching=True)

area = editor.getBuildArea()
editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

player_pos = ivec2(area.size.x // 2, area.size.z // 2)

districts, district_map = generate_districts(SEED, build_rect, world_slice)

for district in districts:
    if not district.is_urban:
        continue

    flatten(district, world_slice, editor)

print('Reloading worldSlice')
world_slice = editor.loadWorldSlice(build_rect)

for x in range(build_rect.size.x):
    for z in range(build_rect.size.y):
        district = district_map[x][z]

        if district is None:
            continue
        
        block = get_color(district, districts)

        place_relative_to_ground(x, 0, z, block, world_slice, editor)

        if ivec2(x, z) in district.edges:
            place_relative_to_ground(x, 1, z, 'glass', world_slice, editor)