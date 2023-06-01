from districts.district import District
from maps.building_map import get_building_map
from maps.water_map import get_water_map
from gdpc import WorldSlice
from gdpc.vector_tools import ivec2, ivec3
from utils.vectors import point_3d
from utils.bounds import is_in_bounds
from utils.bounds import is_in_bounds2d

# class that carries all the different maps required
class Map:
    water : list[list[bool]]
    districts : list[list[District]]
    buildings : list[list[str]]
    world : WorldSlice

    def __init__(self, world_slice : WorldSlice) -> None:
        self.world = world_slice
        self.districts = self.empty_map()
        self.water = get_water_map(world_slice)
        self.buildings = get_building_map(world_slice)

    def correct_district_heights(self, districts : list[District]):
        for district in districts:
            for point in district.points:
                point.y = self.world.heightmaps['MOTION_BLOCKING_NO_LEAVES'][point.x][point.z]

    def empty_map(self):
        size = self.world.rect.size
        return  [[None for _ in range(size.y)] for _ in range(size.x)]
    
    def height_at(self, point : ivec2):
        return self.world.heightmaps['MOTION_BLOCKING_NO_LEAVES'][point.x][point.y]
    
    def make_3d(self, point : ivec2):
        return ivec3(point.x, self.height_at(point), point.y)
    
    def is_in_bounds(self, point : ivec3):
        return is_in_bounds(point, self.world)
    
    def is_in_bounds2d(self, point : ivec2):
        return is_in_bounds2d(point, self.world)