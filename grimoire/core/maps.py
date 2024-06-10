import itertools
from enum import Enum, auto

from gdpc import WorldSlice
from gdpc.block import Block
from gdpc.lookup import ICE_BLOCKS, WATER_PLANTS, WATERS
from gdpc.vector_tools import ivec2, ivec3

from ..districts.district import District
from ..terrain.tree_cutter import TREE_BLOCKS
from .utils.bounds import is_in_bounds, is_in_bounds2d
from .utils.sets.set_operations import find_outline


class DevelopmentType(Enum):
    """
    An enumeration of development types for different structures in a city.

    Attributes:
        HIGHWAY: UNUSED
        WALL: UNUSED
        CITY_ROAD: Represents a city road (surrounding city blocks).
        BUILDING: Is occupied by a building.
        CITY_WALL: Is occupied by a city wall.
        GATE: Is occupied by a gate in the city wall.
    """

    HIGHWAY = auto()  # FIXME: Unused value
    WALL = auto()  # FIXME: Unused value
    CITY_ROAD = auto()
    BUILDING = auto()
    CITY_WALL = auto()
    GATE = auto()


def get_biome_map(world_slice: WorldSlice) -> list[list[str]]:
    size: ivec2 = world_slice.rect.size

    biome_map: list[list[str]] = [["" for _ in range(size.y)] for _ in range(size.x)]

    for x, z in itertools.product(range(size.x), range(size.y)):
        y: int = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][x][z]
        biome: str = world_slice.getBiome((x, y, z))

        biome_map[x][z] = biome

    return biome_map


def get_block_and_water_map(
    world_slice: WorldSlice,
) -> tuple[list[list[Block]], list[list[bool]]]:
    size: ivec2 = world_slice.rect.size

    block_map: list[list[Block]] = [
        [None for _ in range(size.y)] for _ in range(size.x)
    ]
    water_map: list[list[bool]] = [
        [False for _ in range(size.y)] for _ in range(size.x)
    ]

    for x, z in itertools.product(range(size.x), range(size.y)):
        y: int = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][x][z]
        block: Block = world_slice.getBlock((x, y - 1, z))

        if block.id in (WATERS | WATER_PLANTS | ICE_BLOCKS):
            water_map[x][z] = True
        block_map[x][z] = block

    return block_map, water_map


def get_biome_map(world_slice: WorldSlice) -> list[list[str]]:
    size: ivec2 = world_slice.rect.size

    biome_map: list[list[str]] = [["" for _ in range(size.y)] for _ in range(size.x)]

    for x, z in itertools.product(range(size.x), range(size.y)):
        y: int = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][x][z]
        biome: str = world_slice.getBiome((x, y, z))

        biome_map[x][z] = biome

    return biome_map


def get_block_and_water_map(
    world_slice: WorldSlice,
) -> tuple[list[list[Block]], list[list[bool]]]:
    size: ivec2 = world_slice.rect.size

    block_map: list[list[Block]] = [
        [None for _ in range(size.y)] for _ in range(size.x)
    ]
    water_map: list[list[bool]] = [
        [False for _ in range(size.y)] for _ in range(size.x)
    ]

    for x, z in itertools.product(range(size.x), range(size.y)):
        y: int = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][x][z]
        block: Block = world_slice.getBlock((x, y - 1, z))

        if block.id in (WATERS | WATER_PLANTS | ICE_BLOCKS):
            water_map[x][z] = True
        block_map[x][z] = block

    return block_map, water_map


def get_build_map(world_slice: WorldSlice, buffer: int = 0) -> list[list[bool]]:
    """
    Returns a 2D list representing a build map with dimensions extended by the specified buffer size in the x and z directions.

    Args:
        world_slice: The WorldSlice object containing the size information.
        buffer: An integer specifying the additional size to extend the dimensions by (default is 0).

    Returns:
        A 2D list representing the build map with extended dimensions based on the buffer size.
    """

    size: ivec2 = world_slice.rect.size

    return [[False for _ in range(size.y + buffer)] for _ in range(size.x + buffer)]


def get_building_map(world_slice: WorldSlice) -> list[list[DevelopmentType | None]]:
    size: ivec2 = world_slice.rect.size
    return [[None for _ in range(size.y)] for _ in range(size.x)]


def get_water_map(world_slice: WorldSlice) -> list[list[bool]]:
    # NOTE: It would be more efficient to compare the OCEAN_FLOOR and MOTION_BLOCKING heightmaps
    _, water_map = get_block_and_water_map(world_slice)
    return water_map


# class that carries all the different maps required
class Map:
    water: list[list[bool]]
    districts: list[list[District | None]]
    buildings: list[list[DevelopmentType | None]]
    height: list[list[int]]  # height map based on MOTION_BLOCKING_NO_LEAVES
    height_no_tree: list[
        list[int]
    ]  # custom height map based on MOTION_BLOCKING_NO_LEAVES and ignoring wood blocks
    leaf_height: list[list[int]]  # height map based on MOTION_BLOCKING
    world: WorldSlice
    near_wall: list[list[bool]]  # specifically used for routing roads
    highway: list[list[bool]]
    biome: list[list[str]]
    block: list[list[Block]]

    def __init__(self, world_slice: WorldSlice) -> None:
        size = world_slice.rect.size
        self.world = world_slice
        self.districts = self.empty_map()
        self.buildings = get_building_map(world_slice)
        self.biome = get_biome_map(world_slice)
        self.block, self.water = get_block_and_water_map(world_slice)
        self._copy_heightmaps(world_slice)
        self.near_wall = [[False for _ in range(size.y)] for _ in range(size.x)]
        self.highway = [[False for _ in range(size.y)] for _ in range(size.x)]

    def correct_district_heights(self, districts: list[District]):
        # FIXME: Doesn't do anything!
        for district in districts:
            for point in district.points:
                point.y = self.world.heightmaps["MOTION_BLOCKING_NO_LEAVES"][point.x][
                    point.z
                ]

    def empty_map(self) -> list[list[None]]:
        size: ivec2 = self.world.rect.size
        return [[None for _ in range(size.y)] for _ in range(size.x)]

    def block_at(self, point: ivec2) -> Block:
        return self.block[point.x][point.y]

    def biome_at(self, point: ivec2) -> str:
        return self.biome[point.x][point.y]

    def water_at(self, point: ivec2) -> bool:
        return self.water[point.x][point.y]

    def height_at(self, point: ivec2) -> int:
        return self.world.heightmaps["MOTION_BLOCKING_NO_LEAVES"][point.x][point.y]


    def ocean_floor_at(self, point: ivec2):
        return self.world.heightmaps["OCEAN_FLOOR"][point.x][point.y]

    def height_at_include_leaf(self, point: ivec2) -> int:
        return self.world.heightmaps["MOTION_BLOCKING"][point.x][point.y]

    def height_at_not_tree(self, point: ivec2, world_slice: WorldSlice) -> int:
        height: int = self.world.heightmaps["MOTION_BLOCKING_NO_LEAVES"][point.x][
            point.y
        ]
        block: str | None = world_slice.getBlock((point.x, height - 1, point.y)).id
        while block in TREE_BLOCKS:
            height = height - 1
            block = world_slice.getBlock((point.x, height - 1, point.y)).id

        return height

    def _copy_heightmaps(self, world_slice: WorldSlice) -> None:
        size: ivec2 = self.world.rect.size

        self.height, self.leaf_height, self.height_no_tree = [
            [[0 for _ in range(size.y)] for _ in range(size.x)] for _ in range(3)
        ]

        for x, y in itertools.product(range(size.x), range(size.y)):
            self.height[x][y] = self.height_at(ivec2(x, y))
            self.leaf_height[x][y] = self.height_at_include_leaf(ivec2(x, y))
            self.height_no_tree[x][y] = self.height_at_not_tree(
                ivec2(x, y), world_slice
            )

    def make_3d(self, point: ivec2) -> ivec3:
        return ivec3(point.x, self.height_at(point), point.y)

    def is_in_bounds(self, point: ivec3) -> bool:
        return is_in_bounds(point, self.world)

    def is_in_bounds2d(self, point: ivec2) -> bool:
        return is_in_bounds2d(point, self.world)

    def _calculate_near_wall(self, districts: list[District]) -> None:
        urban_area: set[ivec2] = set()

        for district in districts:
            urban_area |= district.points_2d

        near_wall_set: set[ivec2] = find_outline(urban_area, 4) | urban_area

        size: ivec2 = self.world.rect.size
        self.near_wall = [
            [ivec2(x, y) in near_wall_set for y in range(size.y)] for x in range(size.x)
        ]
