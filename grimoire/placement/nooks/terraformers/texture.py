from logging import error
from typing import Iterable, Sequence

from gdpc.block import Block
from gdpc.editor import Editor
from gdpc.lookup import OVERWORLD_SOILS, POLISHED_BLACKSTONE_BRICKS
from gdpc.vector_tools import DOWN_3D, Y_3D, ivec2, ivec3, neighbors2D

from grimoire.core.maps import PATH_DEVELOPMENTS, DevelopmentType, Map
from grimoire.core.noise.rng import RNG
from grimoire.core.styling.palette import BuildStyle
from grimoire.core.utils.misc import growth_spurt
from grimoire.core.utils.shapes import Shape2D
from grimoire.placement.nooks.features.flora import place_tree
from grimoire.placement.nooks.features.manmade import place_statue, place_well
from grimoire.placement.nooks.terraformers.edging import _place_if_development_adjacent

POLISHED_BLACKSTONE_BRICKS_BLOCKS = [Block(b) for b in POLISHED_BLACKSTONE_BRICKS]
DRY_STONE_SLABS = [
    Block(b)
    for b in {
        "minecraft:andesite_slab",
        "minecraft:stone_slab",
        "minecraft:stone_brick_slab",
    }
]
REGULAR_SANDSTONE_SLABS = [
    Block(b)
    for b in {
        "minecraft:sandstone_slab",
        "minecraft:smooth_sandstone_slab",
        "minecraft:cut_sandstone_slab",
        "minecraft:birch_slab",
        "minecraft:cut_sandstone_slab",
    }
]
DEFAULT_PAVING = DRY_STONE_SLABS
DEFAULT_PAVING_DESERT = REGULAR_SANDSTONE_SLABS
DEFAULT_SOIL = Block("minecraft:grass_block")

MATERIALS: dict[BuildStyle, dict[str, str | list[Block]]] = {
    BuildStyle.NORMAL_MEDIEVAL: {
        "paving": DEFAULT_PAVING,
        "wood": "minecraft:spruce",
        "trees": "minecraft:birch",
    },
    BuildStyle.DESERT: {
        "paving": DEFAULT_PAVING_DESERT,
        "wood": "minecraft:birch",
        "trees": "minecraft:oak",
    },
    BuildStyle.WET: {
        "paving": DEFAULT_PAVING,
        "wood": "minecraft:mangrove",
        "trees": "minecraft:cherry",
    },
}

# ==== AREAS ONLY ====


def _pave_area(
    editor: Editor,
    area: Shape2D,
    _edges: dict[ivec2, set[DevelopmentType]],
    style: BuildStyle,
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
    style: BuildStyle,
    city_map: Map,
    _rng: RNG,
) -> None:
    # TODO: Get materials from surrounding streets, then set `fill_blocks`
    return _pave_area(
        editor,
        area,
        edges,
        style,
        city_map,
        _rng,
        fill_blocks=MATERIALS[style]["paving"],
    )


def grass_patch_area(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    style: BuildStyle,
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

    _pave_area(editor, area, edges, style, city_map, _rng, DEFAULT_SOIL)
    return


def wild_growth_area(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    style: BuildStyle,
    city_map: Map,
    _rng: RNG,
) -> None:
    growth: list[Block] = [
        Block(b)
        for b in 1 * ["minecraft:air"]
        + 6 * ["minecraft:grass"]
        + 3 * ["minecraft:poppy", "minecraft:dandelion"]
    ]
    editor.placeBlock(
        [city_map.make_3d(p) for p in area if not city_map.water_at(p)], growth
    )


def trees_in_area(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    style: BuildStyle,
    city_map: Map,
    _rng: RNG,
    positions: Iterable[ivec2] | Iterable[ivec3] | None = None,
    density: float = 0.05,
    tree_type: str | None = None,
):
    if not tree_type:
        tree_type = MATERIALS[style]["trees"]

    if not positions:
        # FIXME: Improve scattering/randomness
        positions = tuple(area)[: int(density * len(area))]
    if not positions:
        return

    if isinstance(positions[0], ivec2):
        positions = [
            city_map.make_3d(p)
            for p in positions
            if city_map.block_at(p) in [Block(b) for b in OVERWORLD_SOILS]
        ]

    place_tree(positions, city_map, editor, tree_type=tree_type)


# ==== EDGES ONLY ====


def grass_edge(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    style: BuildStyle,
    city_map: Map,
    _rng: RNG,
):
    return _pave_area(
        editor,
        Shape2D(set(edges.keys())),
        edges,
        style,
        city_map,
        _rng,
        fill_blocks=Block("minecraft:grass_block"),
    )


def flagstone_edge(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    style: BuildStyle,
    city_map: Map,
    _rng: RNG,
):
    for position, adjacent in edges.items():
        _place_if_development_adjacent(
            editor,
            adjacent,
            PATH_DEVELOPMENTS,
            city_map.make_3d(position) + DOWN_3D,
            Block(f"{MATERIALS[style]['wood']}_wood"),
        )


def roughen_edge(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    style: BuildStyle,
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
            editor.getBlock(city_map.make_3d(neighbour) + DOWN_3D)
            for neighbour in neighbors2D(
                position, area.to_boundry_rect(), diagonal=diagonals
            )
            if neighbour not in edges
        ]

        if not neighbour_blocks:  # search diagonals anyway if nothing was found
            if diagonals:  # This is pointless
                error("Could not find a non-edge neighbour!")
                return
            return roughen_edge(
                editor, area, edges, style, city_map, _rng, diagonals=True
            )

        editor.placeBlock(position3D, neighbour_blocks)
    return


# ==== FULL NOOK ====


def fully_paved(
    editor: Editor,
    area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    style: BuildStyle,
    city_map: Map,
    _rng: RNG,
) -> None:
    return paved_area(editor, area | set(edges.keys()), edges, style, city_map, _rng)


# ==== FEATURE PLACERS ====


def central_statue(
    editor: Editor,
    area: Shape2D,
    _edges: dict[ivec2, set[DevelopmentType]],
    style: BuildStyle,
    city_map: Map,
    rng: RNG,
) -> None:
    return place_statue(editor, city_map.make_3d(area.to_rect().center), rng, city_map)


def central_well(
    editor: Editor,
    area: Shape2D,
    _edges: dict[ivec2, set[DevelopmentType]],
    style: BuildStyle,
    city_map: Map,
    rng: RNG,
) -> None:
    return place_well(editor, city_map.make_3d(area.to_rect().center), rng, city_map)


def boulders(
    editor: Editor,
    area: Shape2D,
    _edges: dict[ivec2, set[DevelopmentType]],
    style: BuildStyle,
    city_map: Map,
    rng: RNG,
) -> None:
    place_boulder(editor, city_map.make_3d(rng.choose(list(area))), rng)
