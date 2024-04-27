import time
from itertools import product as iter_product
from logging import warn
from typing import Optional, Sequence, Union

from gdpc import Block, Editor
from gdpc.lookup import BARKED_LOGS, FOLIAGE, MUSHROOM_BLOCKS, TREE_BLOCKS
from gdpc.vector_tools import ivec2, ivec3
from gdpc.world_slice import WorldSlice

TREE_BLOCKS = (
    BARKED_LOGS
    + MUSHROOM_BLOCKS
    + (
        "minecraft:bamboo",
        "minecraft:mangrove_roots",
        "minecraft:moss_carpet",
        "minecraft:bee_nest",
    )
)

TREE_AND_LEAF_BLOCKS = TREE_BLOCKS + FOLIAGE


def log_stems(editor, build_rect, world_slice):
    return erode(
        editor,
        world_slice,
        heightmap="MOTION_BLOCKING_NO_LEAVES",
        to_replace=TREE_BLOCKS,
    )


def log_trees(editor, build_rect, world_slice):
    return erode(
        editor,
        world_slice,
        heightmap="MOTION_BLOCKING",
        to_replace=TREE_AND_LEAF_BLOCKS,
        to_skip=["minecraft:air"],  # to catch all spruce tree leaves
    )

    # NOTE: If you want the positions of only the tree trunks and branches, use `log_stems` followed by leaf erosion
    # NOTE: If you still wanted to replace the dirt with grass, mycelium, podzol etc., so this:
    # for x, z in erode(...):
    #     # get surface block; if it's dirt replace it based on adjacent blocks


# TODO: Simplify conditions after unit tests have been written
def erode(
    editor: Editor,
    world_slice: WorldSlice,
    *,
    heightmap: str,
    to_replace: Sequence[Block],
    to_skip: Optional[Sequence[Block]] = None,
    stop_at: Optional[Sequence[Block]] = None,
    max_depth: Optional[int] = None,
    replace_with: Union[Block, Sequence[Block]] = Block("minecraft:air"),
) -> set[ivec2]:
    """
    Erode (replace from the surface down) blocks in a world slice based on specified parameters.

    Args:
        editor: The editor object used for modifying the world.
        world_slice: The portion of the world to erode.
        heightmap: The heightmap to use for erosion.
        to_replace: The block or sequence of blocks to replace during erosion.
        to_skip: Blocks to skip during erosion (optional).
        stop_at: Blocks at which to stop erosion (optional).
        replace_with: The block or sequence of blocks to replace with (default is air).

    Raises:
        ValueError: If the provided heightmap is not valid for the WorldSlice.

    Returns:
        set: A set of 2D coordinates representing the affected blocks after erosion.
    """
    if heightmap not in world_slice.heightmaps:
        raise ValueError(
            f"{heightmap} is not a valid heightmap for the provided WorldSlice!"
        )

    lowest_point = world_slice.yBegin

    if max_depth is None:
        max_depth = world_slice.box.size.y

    affected: set[ivec2] = set()

    for x, z in iter_product(world_slice.box.size.x, world_slice.box.size.z):
        y0 = world_slice.heightmaps[heightmap][x][z] - 1
        current_position = ivec3(x, y0, z)
        current_block = world_slice.getBlock(current_position).id

        for y in range(y0, max(lowest_point, y0 - max_depth), -1):
            current_position.y = y

            if current_block in to_replace:
                editor.placeBlock(current_position, replace_with)
                affected.add(ivec2(x, z))
            elif to_skip is None and stop_at is None:
                break
            elif to_skip is not None and current_block in to_skip:
                continue
            elif stop_at is not None and current_block in stop_at:
                break
            elif (
                to_skip is None
                and stop_at is not None
                and current_block not in to_replace
                and current_block not in stop_at
            ):
                continue
            elif (
                to_skip is not None
                and stop_at is None
                and current_block not in to_replace
                and current_block not in to_skip
            ):
                break

            warn(
                f"{current_block} is not covered by parameters and has caused an early stop at {current_position}! Replace will continue as normal."
            )
            break
    return affected


# requires player to fly around to allow minecraft to clear all the foliage, and then set gamerule randomtickspeed to something normal. Still much quicker to clear trees
def manual_clear(editor, build_rect, world_slice):
    tile_drops_off = "gamerule doTileDrops false"
    editor.runCommand(tile_drops_off)

    increase_tick_speed = "gamerule randomTickSpeed 4096"
    editor.runCommand(increase_tick_speed)

    log_stems(editor, build_rect, world_slice)
