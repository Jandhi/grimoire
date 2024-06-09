from typing import Sequence

from gdpc.block import Block
from gdpc.editor import Editor
from gdpc.lookup import POLISHED_BLACKSTONE_BRICKS
from gdpc.vector_tools import neighbors2D
from glm import ivec2, ivec3

from grimoire.core.maps import DevelopmentType, Map
from grimoire.core.noise.rng import RNG
from grimoire.core.utils.shapes import Shape2D

POLISHED_BLACKSTONE_BRICKS_BLOCKS = [Block(b) for b in POLISHED_BLACKSTONE_BRICKS]


def _pave_area(
    editor: Editor,
    area: Shape2D,
    _edges: dict[ivec2, set[DevelopmentType]],
    city_map: Map,
    _rng: RNG,
    fill_blocks: Block | Sequence[Block] = POLISHED_BLACKSTONE_BRICKS_BLOCKS,
) -> None:
    """
    Paves the specified area with the given fill blocks.

    Args:
        editor: The Editor object for placing blocks.
        area: The 2D shape area to be paved.
        city_map: The Map object representing the city map.
        fill_blocks: The block or sequence of blocks to fill the area with (default is POLISHED_BLACKSTONE_BRICKS).

    Returns:
        None
    """
    for position in area:
        position3D: ivec3 = city_map.make_3d(position)
        editor.placeBlock(position3D, fill_blocks)
    return


def pave_over_area(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    city_map: Map,
    _rng: RNG,
) -> None:
    # TODO: Get materials from surrounding streets, then set `fill_blocks`
    return _pave_area(editor, area, edges, city_map, _rng)


def grass_patch_area(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    city_map: Map,
    _rng: RNG,
) -> None:
    """
    Creates a grass patch within the specified area by placing grass blocks and surrounding blocks.
    TODO: Bonemeal the surrounding substrate to

    Args:
        editor:   The Editor object for placing blocks.
        area:     The 2D shape area to create the grass patch.
        edges:    The positions and adjacent DevelopmentTypes of the edges.
        city_map: The Map object representing the city map.

    Returns:
        None
    """

    SOIL: list[Block] = [Block(b) for b in {"minecraft:grass"}]

    _pave_area(editor, area, edges, city_map, _rng, SOIL)
    # TODO: bonemeal(position3D)
    return


def roughen_edge(
    editor: Editor,
    _area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    city_map: Map,
    _rng: RNG,
    diagonals: bool = False,
) -> None:
    """
    Roughens the edges of the specified area by placing random neighboring blocks.

    Args:
        editor:    The Editor object for placing blocks.
        edges:    The positions and adjacent DevelopmentTypes of the edges.
        city_map:  The Map object representing the city map.
        diagonals: Whether to initially consider diagonal in addition to orthogonal neighbors (default is False).

    Returns:
        None
    """

    # populate edges with random samples from the surroundings
    for position in edges:
        position3D = city_map.make_3d(position)

        # get neighboring Blocks which aren't part of the edge
        neighbour_blocks: set[Block] = {
            editor.getBlock(city_map.make_3d(neighbour))
            for neighbour in neighbors2D(position, diagonal=diagonals)
            if neighbour not in edges
        }

        if not neighbour_blocks:  # search diagonals anyway if nothing was found
            if diagonals:  # This is pointless
                raise RuntimeError("Could not find a non-edge neighbour!")
            return roughen_edge(editor, _area, edges, city_map, _rng, diagonals=True)

        editor.placeBlock(position3D, neighbour_blocks)
    return
