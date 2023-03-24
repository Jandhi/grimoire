from districts.district import District
from gdpc import Editor, WorldSlice, Block
from gdpc.vector_tools import ivec2, ivec3

def flatten(district : District, district_map : list[list[District]], world_slice : WorldSlice, editor : Editor, water_map : list[list[bool]]):
    print(f'Flattening {district}')
    updated_heights = dict()

    for x, y, z in district.points:
        key = x, z

        district_at_point = district_map[x][z]

        # we don't want to flatten water tiles
        if water_map[x][z]:
            continue

        # we only want to consider points that are in the district or in adjacent districts
        if district_at_point == district or (district_at_point in district.adjacency and district.adjacency[district_at_point] > 0):
            updated_heights[key] = (average_neighbour_height(x, z, district, world_slice))

    for key in updated_heights:
        y = updated_heights[key]
        x, z = key
        set_height(x, y, z, world_slice, editor)

    update_district_points(district, world_slice)

RANGE = 10
NEIGHBOURS = [(x, z) for x in range(-RANGE, RANGE + 1) for z in range(-RANGE, RANGE + 1)]

def average_neighbour_height(x : int, z : int, district : District, world_slice : WorldSlice) -> int:
    height_sum = 0
    total_weight = 0

    for dx, dz in NEIGHBOURS:
        if ivec2(x + dx, z + dz) not in district.points_2d: # we only need to flatten for within a district
            continue

        distance = abs(dx) + abs(dz)
        weight = 0.8 ** distance
        height = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x + dx][z + dz]
        height_sum += height * weight
        total_weight += weight

    return round(height_sum / total_weight)

def set_height(x : int, y : int, z : int, world_slice : WorldSlice, editor : Editor):
    curr_y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z]
    block = world_slice.getBlock((x, curr_y - 1, z))

    if curr_y > y:
        for py in range(y, curr_y):
            editor.placeBlock((x, py, z), Block('air'))

        editor.placeBlock((x, y-1, z), block)
    elif curr_y < y:
        
        for py in range(curr_y, y):
            editor.placeBlock((x, py, z), block)

# updates the points set of a district to be correct
def update_district_points(district : District, world_slice : WorldSlice):
    district.points.clear()
    sum_point = ivec3(0, 0, 0)
    
    for x, z in district.points_2d:
        y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z]
        point = ivec3(x, y, z)
        district.points.add(point)
        sum_point += point