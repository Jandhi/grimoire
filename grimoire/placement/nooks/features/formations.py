from gdpc.vector_tools import ivec3

from grimoire.core.noise.rng import RNG
from grimoire.core.structures.asset_structure import AssetStructure
from grimoire.core.structures.nbt.build_nbt import build_nbt
from grimoire.core.structures.transformation import Transformation


def place_boulder(editor, position: ivec3, rng: RNG):
    statue = rng.choose([s for s in AssetStructure.all() if "boulder" in s.name])
    build_nbt(
        editor, statue, palette=None, transformation=Transformation(offset=position)
    )
