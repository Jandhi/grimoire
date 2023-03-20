from gdpc import WorldSlice, Editor, Block

def place_relative_to_ground(x : int, y : int, z : int, block_name : str, world_slice : WorldSlice, editor : Editor):
    y_offset = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z] - 1
    editor.placeBlock((x, y + y_offset, z), Block(block_name))

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