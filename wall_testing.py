from gdpc import Editor, Block
from gdpc.vector_tools import ivec2
from districts.generate_districts import generate_districts
from utils.geometry import get_outer_points
from districts.wall import build_wall_palisade, order_wall_points
from noise.rng import RNG
from noise.random import choose_weighted

editor = Editor(buffering=True, caching=True)

area = editor.getBuildArea()
editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

def place_at_ground(x, z, block_name):
    y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z]
    editor.placeBlock((x, y - 1, z), Block(block_name))

def replace_ground(points: list[ivec2], block_dict: dict[any,int], rng):
    for point in points:
        block = choose_weighted(rng.value(), block_dict)
        place_at_ground(point.x, point.y, block)

test_blocks = {
    'stone': 3,
    'cobblestone' : 2,
    'stone_bricks' : 8,
    'andesite' : 3,
    'gravel' : 1
}

player_pos = ivec2(area.size.x // 2, area.size.z // 2)

districts, district_map = generate_districts(build_rect, world_slice)

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
def get_color(index):
    return colors[index % len(colors)] + '_wool'

inner_points = []

for x in range(build_rect.size.x):
    for z in range(build_rect.size.y):
        district = district_map[x][z]

        if district is None:
            continue
        elif district.inner:
            inner_points.append(ivec2(x,z))

        index = districts.index(district)
        block = get_color(index)

        place_at_ground(x, z, block)

for district in districts:
    x = district.origin.x
    z = district.origin.y

    y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z] + 10
    #editor.placeBlock((x, y, z), Block('sea_lantern'))


wall_points, wall_dict = get_outer_points(inner_points, world_slice)
wall_points = order_wall_points(wall_points, wall_dict)

rng = RNG(0)

build_wall_palisade(wall_points, editor, world_slice, rng)

replace_ground(inner_points, test_blocks, rng)

#for point in wall_points:
#    y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z]
#    editor.placeBlock((point.x, y, point.y), Block('coal_block'))

    #setbuildarea ~ 0 ~ ~256 255 ~256