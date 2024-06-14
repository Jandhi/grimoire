from gdpc import Editor
from gdpc.block import Block
from gdpc.vector_tools import ivec2

from grimoire.core.maps import DevelopmentType, Map
from grimoire.core.noise.rng import RNG
from grimoire.core.utils.shapes import Shape2D


def simple_closed_fencing(
    editor: Editor,
    _area: Shape2D,
    edges: dict[ivec2, set[DevelopmentType]],
    city_map: Map,
    _rng: RNG,
    fence_block: Block = Block("minecraft:oak_fence"),
):
    for position, adjacent in edges.items():
        # TODO: be selective about which block to place
        editor.placeBlock(city_map.make_3d(position), fence_block)
