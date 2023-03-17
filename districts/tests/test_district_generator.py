# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\districts\\tests')

# Actual file
from gdpc import Editor, Block
from gdpc.vector_tools import ivec2
from districts.generate_districts import generate_districts


SEED = 36322

editor = Editor(buffering=True, caching=True)

area = editor.getBuildArea()
editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

def place_relative_to_ground(x, y, z, block_name):
    y_offset = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z]
    editor.placeBlock((x, y_offset, z), Block(block_name))

player_pos = ivec2(area.size.x // 2, area.size.z // 2)

districts, district_map = generate_districts(SEED, build_rect, world_slice)

colors = [
    'white',
    'orange',
    'magenta', 
    'light_blue', 
    'yellow', 
    'lime', 
    'pink', 
    'gray', 
    'light_gray', 
    'cyan', 
    'purple', 
    'blue', 
    'brown', 
    'green', 
    'red', 
    'black'
]

urban_districts_blocks = [
    'polished_andesite',
    'polished_granite',
    'polished_diorite',
    'polished_deepslate',
    'nether_bricks',
    'stone_bricks',
    'red_nether_bricks',
    'polished_blackstone',
]
rural_districts_blocks = [
    'grass_block',
    'dirt',
    'podzol',
    'sand',
    'mycelium',
]

def get_color(district, districts):
    blocks = colors #urban_districts_blocks if district.is_urban else rural_districts_blocks
    return blocks[districts.index(district) % len(blocks)] + '_wool'

for x in range(build_rect.size.x):
    for z in range(build_rect.size.y):
        district = district_map[x][z]

        if district is None:
            continue
        
        block = get_color(district, districts)

        place_relative_to_ground(x, -1, z, block)

        if ivec2(x, z) in district.edges:
            place_relative_to_ground(x, 0, z, 'glass')

for district in districts:
    x = district.origin.x
    z = district.origin.y

    y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z] + 10
    editor.placeBlock((x, y, z), Block('sea_lantern'))