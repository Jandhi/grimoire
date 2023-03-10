from gdpc import Editor, Block
from gdpc.vector_tools import ivec2
from districts.generate_districts import generate_districts

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

for x in range(build_rect.size.x):
    for z in range(build_rect.size.y):
        district = district_map[x][z]

        if district is None:
            continue

        index = districts.index(district)
        block = get_color(index)

        place_at_ground(x, z, block)

for district in districts:
    x = district.origin.x
    z = district.origin.y

    y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z] + 10
    editor.placeBlock((x, y, z), Block('sea_lantern'))