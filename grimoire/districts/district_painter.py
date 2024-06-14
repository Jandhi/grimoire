import itertools
import time

from gdpc import Block, Editor, WorldSlice
from gdpc.vector_tools import ivec2, ivec3

from ..core.maps import Map, DevelopmentType
from ..core.noise.random import choose_weighted, shuffle
from ..core.noise.rng import RNG
from ..core.structures.legacy_directions import CARDINAL, get_ivec2, to_text
from ..terrain.forest import Forest
from ..terrain.tree import generate_tree


# gives the ability to provide a list of blocks upon which not to place
def replace_ground(
    points: list[ivec2],
    block_dict: dict[any, int],
    rng: RNG,
    water_map: list[list[bool]],
    build_map: list[list[bool]],
    editor: Editor,
    world_slice: WorldSlice,
    height_offset: int = 0,
    ignore_blocks: list = [],
    ignore_water: bool = False,
):
    for counter, point in enumerate(points, start=1):
        if (ignore_water or water_map[point.x][point.y] == False) and build_map[
            point.x
        ][point.y] == False:
            y = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][point.x][point.y]
            if editor.getBlock(ivec3(point.x, y - 1, point.y)).id not in ignore_blocks:
                block = choose_weighted(rng.value(), block_dict)
                editor.placeBlock(
                    (point.x, y - 1 + height_offset, point.y), Block(block)
                )


# requires the block dict to have 3 dicts inside, blocks, slabs, stairs
def replace_ground_smooth(
    points: list[ivec2],
    block_dict: dict[any, int],
    rng: RNG,
    build_map: Map,
    editor: Editor,
    height_offset: int = 0,
    ignore_blocks: list = [],
    ignore_water: bool = False,
):
    for counter, point in enumerate(points, start=1):
        if (ignore_water or not build_map.water_at(point)) and (
            not build_map.buildings[point.x][point.y]
            or build_map.buildings[point.x][point.y] == DevelopmentType.CITY_ROAD
        ):
            y = build_map.height_at(point)
            if editor.getBlock(ivec3(point.x, y - 1, point.y)).id not in ignore_blocks:
                # decide on slab/stair/block
                block = None
                y_in_dir = {}

                for direction in CARDINAL:
                    delta = get_ivec2(direction)
                    neighbour = point + delta
                    opposite_neighbour = point - delta

                    if neighbour in points:
                        y_in_dir[direction] = build_map.height_at(neighbour)

                    if (
                        build_map.height_at(neighbour) == y + 1
                        and build_map.height_at(opposite_neighbour) == y - 1
                    ):
                        block = (
                            choose_weighted(rng.value(), block_dict["stairs"])
                            + f"[facing={to_text(direction)}]"
                        )
                        break

                if all(y_in_dir[direction] <= y for direction in y_in_dir) and any(
                    y_in_dir[direction] < y for direction in y_in_dir
                ):
                    block = choose_weighted(rng.value(), block_dict["slabs"])

                if block is None:
                    block = choose_weighted(rng.value(), block_dict["blocks"])

                editor.placeBlock(
                    (point.x, y - 1 + height_offset, point.y), Block(block)
                )


def plant_forest(
    points: list[ivec2],
    forest: Forest,
    rng: RNG,
    water_map: list[list[bool]],
    build_map: list[list[bool]],
    editor: Editor,
    world_slice: WorldSlice,
    ignore_blocks: list = [],
    ignore_water: bool = False,
):
    points = shuffle(rng.value(), points)
    for point in points:
        if (ignore_water or water_map[point.x][point.y] == False) and build_map[
            point.x
        ][point.y] == False:
            y = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][point.x][point.y]
            if editor.getBlock(ivec3(point.x, y - 1, point.y)).id not in ignore_blocks:
                tree_type = choose_weighted(rng.value(), forest.tree_dict)
                generate_tree(
                    tree_type,
                    ivec3(point.x, y, point.y),
                    editor,
                    forest.tree_palette[tree_type],
                )
                for a, b in itertools.product(
                    range(
                        point.x - forest.tree_density + 1, point.x + forest.tree_density
                    ),
                    range(
                        point.y - forest.tree_density + 1, point.y + forest.tree_density
                    ),
                ):
                    build_map[a][b] = True
