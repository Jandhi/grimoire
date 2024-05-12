from districts.district import District
from maps.building_map import get_building_map
from maps.water_map import get_water_map
from maps.biome_map import get_biome_map
from maps.block_map import get_block_and_water_map
from gdpc import WorldSlice
from gdpc.vector_tools import ivec2, ivec3
from utils.vectors import point_3d
from utils.bounds import is_in_bounds
from utils.bounds import is_in_bounds2d
from sets.set_operations import find_outline
from gdpc import Block
from terrain.logger import TREE_BLOCKS

# class that carries all the different maps required
class Map:
    water : list[list[bool]]
    districts : list[list[District]]
    buildings : list[list[str]]
    height : list[list[int]] # height map based on MOTION_BLOCKING_NO_LEAVES
    height_no_tree : list[list[int]] # custom height map based on MOTION_BLOCKING_NO_LEAVES and ignoring wood blocks
    leaf_height : list[list[int]] # height map based on MOTION_BLOCKING
    #new height map to be height map based on no trees/structures etc
    world : WorldSlice
    near_wall : list[list[bool]] # specifically used for routing roads 
    biome: list[list[str]]
    block: list[list[Block]]

    def __init__(self, world_slice : WorldSlice) -> None:
        self.world = world_slice
        self.districts = self.empty_map()
        self.buildings = get_building_map(world_slice)
        self.biome = get_biome_map(world_slice)
        self.block, self.water = get_block_and_water_map(world_slice)
        self.copy_heightmaps(world_slice)

    def correct_district_heights(self, districts : list[District]):
        for district in districts:
            for point in district.points:
                point.y = self.world.heightmaps['MOTION_BLOCKING_NO_LEAVES'][point.x][point.z]

    def empty_map(self):
        size = self.world.rect.size
        return  [[None for _ in range(size.y)] for _ in range(size.x)]
    
    def height_at(self, point : ivec2):
        return self.world.heightmaps['MOTION_BLOCKING_NO_LEAVES'][point.x][point.y]
    
    def copy_heightmaps(self, world_slice : WorldSlice):
        size = self.world.rect.size
        self.height = [[self.height_at(ivec2(x, y)) for y in range(size.y)] for x in range(size.x)]
        self.leaf_height = [[self.height_at_include_leaf(ivec2(x, y)) for y in range(size.y)] for x in range(size.x)]
        self.height_no_tree = [[self.height_at_not_tree(ivec2(x, y), world_slice) for y in range(size.y)] for x in range(size.x)]

    def height_at_include_leaf(self, point : ivec2):
        return self.world.heightmaps['MOTION_BLOCKING'][point.x][point.y]
    
    def height_at_not_tree(self, point : ivec2, world_slice : WorldSlice):
        height = self.world.heightmaps['MOTION_BLOCKING_NO_LEAVES'][point.x][point.y]
        block = world_slice.getBlock((point.x,height-1,point.y)).id
        while block in TREE_BLOCKS:
            height = height - 1
            block = world_slice.getBlock((point.x,height-1,point.y)).id

        return height
    
    def make_3d(self, point : ivec2):
        return ivec3(point.x, self.height_at(point), point.y)
    
    def is_in_bounds(self, point : ivec3):
        return is_in_bounds(point, self.world)
    
    def is_in_bounds2d(self, point : ivec2):
        return is_in_bounds2d(point, self.world)
    
    def calculate_near_wall(self, districts : list[District]):
        urban_area = set()

        for district in districts:
            urban_area |= district.points_2d

        near_wall_set = find_outline(urban_area, 4) | urban_area

        size = self.world.rect.size
        self.near_wall = [[ivec2(x, y) in near_wall_set for y in range(size.y)] for x in range(size.x)]

    def block_at(self, point: ivec2) -> Block:
        return self.block[point.x][point.y]
    
    def biome_at(self, point: ivec2) -> str:
        return self.biome[point.x][point.y]
    
    def water_at(self, point: ivec2) -> bool:
        return self.water[point.x][point.y]