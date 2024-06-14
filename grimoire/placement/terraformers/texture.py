from logging import error
from typing import Sequence

from gdpc.block import Block
from gdpc.editor import Editor
from gdpc.lookup import POLISHED_BLACKSTONE_BRICKS
from gdpc.vector_tools import DOWN_3D, Y_3D, neighbors2D
from glm import ivec2, ivec3

from grimoire.core.maps import DevelopmentType, Map
from grimoire.core.noise.rng import RNG
from grimoire.core.utils.misc import growth_spurt
from grimoire.core.utils.shapes import Shape2D

POLISHED_BLACKSTONE_BRICKS_BLOCKS = [Block(b) for b in POLISHED_BLACKSTONE_BRICKS]
DRY_STONE_BRICK_SLABS = [
    Block(b)
    for b in {"minecraft:cracked_stone_brick_slab", "minecraft:stone_brick_slab"}
]
REGULAR_SANDSTONE_SLABS = [
    Block(b)
    for b in {
        "minecraft:sandstone_slab",
        "minecraft:sandstone_slab",
        "minecraft:cut_sandstone_slab",
    }
]
DEFAULT_PAVING = DRY_STONE_BRICK_SLABS
DEFAULT_PAVING_DESERT = REGULAR_SANDSTONE_SLABS
DEFAULT_SOIL = Block("minecraft:grass_block")

# ==== AREAS ONLY ====


def _pave_area(
    editor: Editor,
    area: Shape2D,
    _edges: dict[ivec2, set[DevelopmentType]],
    city_map: Map,
    _rng: RNG,
    fill_blocks: Block | Sequence[Block] = DEFAULT_PAVING,
    pave_liquids: bool = False,
    y_offset: int = 0,
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
        if not pave_liquids and city_map.water_at(position):  # ignore water
            continue
        position3D: ivec3 = city_map.make_3d(position) + DOWN_3D + y_offset * Y_3D
        editor.placeBlock(position3D, fill_blocks)
    return


def paved_area(
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

    _pave_area(editor, area, edges, city_map, _rng, DEFAULT_SOIL)
    return


def wild_growth_area(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    city_map: Map,
    _rng: RNG,
):
    growth: list[Block] = [
        Block(b)
        for b in 11 * ["minecraft:air"]
        + 75 * ["minecraft:grass"]
        + 7 * ["minecraft:poppy", "minecraft:dandelion"]
        + ["minecraft:oak_sapling"]
    ]
    editor.placeBlock([city_map.make_3d(p) for p in area], growth)
    growth_spurt(editor)


# ==== EDGES ONLY ====


def grass_edge(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    city_map: Map,
    _rng: RNG,
):
    return _pave_area(
        editor,
        Shape2D(set(edges.keys())),
        edges,
        city_map,
        _rng,
        fill_blocks=Block("minecraft:grass_block"),
    )


def flagstone_edge(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    city_map: Map,
    _rng: RNG,
):
    return _pave_area(
        editor,
        Shape2D(set(edges.keys())),
        edges,
        city_map,
        _rng,
        fill_blocks=Block("minecraft:smooth_stone"),
    )


def roughen_edge(
    editor: Editor,
    area: Shape2D,
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
        position3D = city_map.make_3d(position) + DOWN_3D

        # get neighboring Blocks which aren't part of the edge
        neighbour_blocks: list[Block] = [
            editor.getBlock(city_map.make_3d(neighbour))
            for neighbour in neighbors2D(
                position, area.to_boundry_rect(), diagonal=diagonals
            )
            if neighbour not in edges
        ]

        if not neighbour_blocks:  # search diagonals anyway if nothing was found
            if diagonals:  # This is pointless
                error("Could not find a non-edge neighbour!")
                return
            return roughen_edge(editor, area, edges, city_map, _rng, diagonals=True)

        editor.placeBlock(position3D, neighbour_blocks)
    return


# ==== FULL NOOK ====


def fully_paved(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    city_map: Map,
    _rng: RNG,
) -> None:
    return _pave_area(editor, area | set(edges.keys()), edges, city_map, _rng)


def fully_paved_desert(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    city_map: Map,
    _rng: RNG,
) -> None:
    return _pave_area(
        editor, area | set(edges.keys()), edges, city_map, _rng, DEFAULT_PAVING_DESERT
    )
