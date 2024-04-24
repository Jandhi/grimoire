from gdpc import WorldSlice

HIGHWAY = "highway"  # FIXME: Unused variable
CITY_ROAD = "city_road"
BUILDING = "building"
WALL = "Wall"  # FIXME: Unused variable
CITY_WALL = "city_wall"
GATE = "gate"


def get_building_map(world_slice: WorldSlice):
    size = world_slice.rect.size
    return [[None for _ in range(size.y)] for _ in range(size.x)]
