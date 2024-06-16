from typing import Sequence

from gdpc import Editor
from gdpc.block import Block
from gdpc.vector_tools import ivec2, ivec3

from grimoire.core.maps import PATH_DEVELOPMENTS, DevelopmentType, Map
from grimoire.core.noise.rng import RNG
from grimoire.core.styling.palette import BuildStyle
from grimoire.core.utils.shapes import Shape2D

MATERIALS: dict[BuildStyle, dict[str, str | list[Block]]] = {
    BuildStyle.NORMAL_MEDIEVAL: {
        "wood": "minecraft:spruce",
        "trees": "minecraft:birch",
    },
    BuildStyle.DESERT: {
        "wood": "minecraft:birch",
        "trees": "minecraft:oak",
    },
    BuildStyle.WET: {
        "wood": "minecraft:mangrove",
        "trees": "minecraft:cherry",
    },
}


def _place_if_development_adjacent(
    editor: Editor,
    adjacent: set[DevelopmentType],
    development_set: set[DevelopmentType] | frozenset[DevelopmentType],
    position: ivec3,
    block: Block | Sequence[Block],
    replace: str | list[str] | None = None,
):
    if adjacent & development_set:
        return editor.placeBlock(position, block, replace)
    return False


def simple_closed_fencing(
    editor: Editor,
    _area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    style: BuildStyle,
    city_map: Map,
    _rng: RNG,
    fence_block: Block = None,
):
    if not fence_block:
        fence_block = Block(f"{MATERIALS[style]['wood']}_fence")
    for position, adjacent in edges.items():
        _place_if_development_adjacent(
            editor, adjacent, PATH_DEVELOPMENTS, city_map.make_3d(position), fence_block
        )
