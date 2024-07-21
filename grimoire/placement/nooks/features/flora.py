from logging import error
from typing import Iterable

from gdpc import Editor
from gdpc.block import Block
from gdpc.vector_tools import Box, Rect, ivec3

from grimoire.core.maps import Map

DEFAULT_TREE_TYPE = "minecraft:oak"


def place_tree(
    positions_3D: Iterable[ivec3] | ivec3,
    city_map: Map,
    editor: Editor,
    tree_type: str | None = None,
    space: Box | Rect | None = None,
):
    if isinstance(positions_3D, ivec3):
        positions_3D = [positions_3D]

    if not tree_type:
        tree_type = DEFAULT_TREE_TYPE

    if isinstance(tree_type, str):
        # TODO: Replace sapling-placement with fully grown trees
        try:
            editor.placeBlock(positions_3D, Block(f"{tree_type}_sapling"))
        except Exception as e:
            error(f"Failed to place '{tree_type}_sapling' at {positions_3D}:\n{e}")
    else:
        # TODO
        raise NotImplementedError("Custom trees are not yet supported!")
