from typing import Sequence

from gdpc.block import Block
from gdpc.editor import Editor
from gdpc.geometry import placeCuboid
from gdpc.vector_tools import addY, neighbors3D
from glm import ivec2, ivec3

from grimoire.core.maps import DevelopmentType, Map
from grimoire.core.noise.rng import RNG
from grimoire.core.styling.materials.material import Material
from grimoire.core.utils.shapes import Shape2D

# ==== Completely flatten ====


def flatten_area_up(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    city_map: Map,
    rng: RNG,
) -> None:
    """
    Flattens the specified area up to the maximum y-coordinate of the edges.

    Args:
        editor:   The Editor object for placing blocks.
        area:     The 2D shape area to be flattened.
        edges:    The positions and adjacent DevelopmentTypes of the edges.
        city_map: The Map object representing the city map.
        rng:      UNUSED (follows terraform function template)

    Returns:
        None
    """

    goal_y: int = editor.worldSlice.box.end.y  # top of World Slice

    for position in edges:
        goal_y = max(goal_y, position.y)

    return _flatten_area_to(editor, area, edges, city_map, rng, goal_y)


def flatten_area_down(
    editor,
    area,
    edges,
    city_map,
    rng,
) -> None:
    """
    Flattens the specified area down to the minimum y-coordinate of the edges.

    Args:
        editor:   The Editor object for placing blocks.
        area:     The 2D shape area to be flattened.
        edges:    The positions and adjacent DevelopmentTypes of the edges.
        city_map: The Map object representing the city map.
        rng:      UNUSED (follows terraform function template)

    Returns:
        None
    """

    goal_y: int = editor.worldSlice.box.end.y  # top of World Slice

    for position in edges:
        goal_y = min(goal_y, position.y)

    return _flatten_area_to(editor, area, edges, city_map, rng, goal_y)


def _flatten_area_to(
    editor,
    area,
    edges,
    city_map,
    rng,
    goal_y=63,
    fill_block=None,
) -> None:
    """
    Flattens the specified area to the given goal y-coordinate by placing blocks.

    Args:
        editor:     The Editor object for placing blocks.
        area:       The 2D shape area to be flattened.
        edges:      UNUSED (follows terraform function template)
        city_map:   The Map object representing the city map.
        rng:        UNUSED (follows terraform function template)
        goal_y:     The target y-coordinate to flatten the area to (default is sea level).
        fill_block: The block or sequence of blocks to fill the area with (default is block beneath).

    Returns:
        None
    """

    for position in area:
        position3D: ivec3 = city_map.make_3d(position)
        if position3D.y == goal_y:
            continue

        place_block: Block = "minecraft:air"
        offset = 1  # remove everything above the goal

        if position3D.y < goal_y:  # fill up to y goal instead
            # fill with the block beneath if no fill block is defined
            place_block = (
                editor.getBlock(position3D) if fill_block is None else fill_block
            )
            offset = 0

        placeCuboid(editor, position3D, addY(position, goal_y + offset), place_block)
