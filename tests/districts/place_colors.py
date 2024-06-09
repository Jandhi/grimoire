from gdpc import Block, Editor

from grimoire.core.maps import Map
from grimoire.districts.district import District


def place_relative_to_ground(
    x: int, y: int, z: int, block_name: str, main_map: Map, editor: Editor
) -> None:
    y_offset: int = main_map.height_no_tree[x][z] - 1
    editor.placeBlock((x, y + y_offset, z), Block(block_name))


colors: list[str] = [
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


def get_color(district: District, districts: list[District]) -> str:
    blocks: list[str] = colors
    return f"{blocks[districts.index(district) % len(blocks)]}_wool"


def get_color_differentiated(
    district: District, districts: list[District], is_water: bool
) -> str:
    blocks: list[str] = colors
    suffix = "_terracotta"

    if is_water:
        suffix = "_stained_glass"
    elif district.is_urban:
        suffix = "_wool"

    return blocks[districts.index(district) % len(blocks)] + suffix
