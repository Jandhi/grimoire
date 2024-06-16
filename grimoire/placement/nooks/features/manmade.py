from gdpc.vector_tools import ivec3

from grimoire.core.maps import Map, DevelopmentType
from grimoire.core.noise.rng import RNG
from grimoire.core.structures.asset_structure import AssetStructure
from grimoire.core.structures.nbt.build_nbt import build_nbt
from grimoire.core.structures.transformation import Transformation


def place_statue(editor, position: ivec3, rng: RNG, city_map: Map):
    statues: list[AssetStructure] = rng.shuffle(
        [s for s in AssetStructure.all() if "statue" in s.name]
    )

    for statue in statues:
        buildable = 0
        unbuildable_count = 0

        for x in range(statue.size.x):
            for z in range(statue.size.z):
                if (
                    city_map.buildings[x + position.x][z + position.z]
                    == DevelopmentType.BUILDING
                    or city_map.buildings[x + position.x][z + position.z]
                    == DevelopmentType.CITY_WALL
                    or city_map.water[x + position.x][z + position.z]
                ):
                    unbuildable_count += 1
                else:
                    buildable += 1

        if unbuildable_count > 10:
            continue

        build_nbt(
            editor, statue, palette=None, transformation=Transformation(offset=position)
        )

        return
