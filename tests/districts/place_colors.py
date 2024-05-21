from gdpc import WorldSlice, Editor, Block
from grimoire.core.maps import Map

def place_relative_to_ground(x : int, y : int, z : int, block_name : str, map : Map, editor : Editor):
    y_offset = map.height_no_tree[x][z] - 1
    editor.placeBlock((x, y + y_offset, z), Block(block_name))


colors = [
    "white",
    "orange",
    "magenta",
    "light_blue",
    "yellow",
    "lime",
    "pink",
    "gray",
    "light_gray",
    "cyan",
    "purple",
    "blue",
    "brown",
    "green",
    "red",
    "black",
]


def get_color(district, districts):
    blocks = colors
    return f"{blocks[districts.index(district) % len(blocks)]}_wool"


def get_color_differentiated(district, districts, is_water):
    blocks = colors
    suffix = "_terracotta"

    if is_water:
        suffix = "_stained_glass"
    elif district.is_urban:
        suffix = "_wool"

    return blocks[districts.index(district) % len(blocks)] + suffix
