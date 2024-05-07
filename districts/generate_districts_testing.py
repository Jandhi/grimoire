from noise.rng import RNG
from districts.district import District
from gdpc.vector_tools import Rect, ivec2, distance, ivec3
from structures.legacy_directions import cardinal, vector
from gdpc import WorldSlice
from districts.adjacency import establish_adjacency
from districts.merging_districts import merge_down
from maps.map import Map
from districts.district_analyze import district_analyze

# from districts.adjacency import establish_adjacency, get_neighbours
CHUNK_SIZE = 16
TARGET_POINTS_GENERATED = 36
TARGET_DISTRICT_AMT = 10
OUTER_POINTS_MIN_DISTANCE = 10
INNER_POINTS_MIN_DISTANCE = 5
RETRIES = 100
INNER_DISTRICTS_AMOUNT_RATIO = 0.5
INNER_DISTRICTS_TARGET_AREA = 0.3 # The ratio of area where inner districts spawn
CHOKEPOINT_ADJACENCY_RATIO = 0.3 # If this percent or less of an urban district touches other urban district, it is pruned

def generate_districts(seed : int, build_rect : Rect, world_slice : WorldSlice, map : Map):
    districts = spawn_districts(seed, build_rect, world_slice)
    district_map : list[list[District]] = [[None for _ in range(build_rect.size.y)] for _ in range(build_rect.size.x)]

    for district in districts:
        origin = district.origin
        district_map[origin.x][origin.z] = district

    bubble_out(world_slice, districts, district_map, map.water)
    
    for i in range(0, 2):
        district_map = [[None for _ in range(build_rect.size.y)] for _ in range(build_rect.size.x)]
        recalculate_center_point(world_slice, districts, district_map, map.water)

        bubble_out(world_slice, districts, district_map, map.water)
    
    establish_adjacency(world_slice, district_map)
    for district in districts:
        district_analyze(district, map)
    merge_down(districts, district_map, TARGET_DISTRICT_AMT, map)
    

    # remeasure adjacency after
    for district in districts:
        district.adjacency = {}
        district.adjacencies_total = 0
    establish_adjacency(world_slice, district_map)

    prune_urban_chokepoints(districts)

    return (districts, district_map)

def recalculate_center_point(world_slice : WorldSlice, districts : list[District], district_map : list[list[District]], water_map : list[list[bool]]):
    print("finding center point again")
    

    for district in districts:
        origin = district.average() # assumes no heigh deviation
        district.recenter(origin)
        district_map[origin.x][origin.z] = district
    


def bubble_out(world_slice : WorldSlice, districts : list[District], district_map : list[list[District]], water_map : list[list[bool]]):
    #additional value added which defines how many iterations needed to claim the block
    queue = [[district.origin, 0] for district in districts]
    water_queue = []
    visited = {district.origin for district in districts}

    def add_point_to_district(point : ivec3, district : District):
        district_map[point.x][point.z] = district
        district.add_point(point)

    # first pass normal queue
    while len(queue) > 0:
        next = queue.pop(0)
        point = next[0]
        district = district_map[point.x][point.z]

        if next[1] > 0:
            queue.append([point, next[1]-1])
        else:
            for neighbour in get_neighbours(point, world_slice):
                if neighbour[0] in visited:
                    continue

                visited.add(neighbour[0])
                add_point_to_district(neighbour[0], district)
                
                if water_map[neighbour[0].x][neighbour[0].z]:
                    water_queue.append(neighbour[0])
                else:
                    queue.append(neighbour)
    
    # second pass water queue
    while len(water_queue) > 0:
        point = water_queue.pop(0)
        district = district_map[point.x][point.z]

        for neighbour in get_neighbours(point, world_slice):
            if neighbour[0] in visited:
                continue

            visited.add(neighbour[0])
            water_queue.append(neighbour[0])
            add_point_to_district(neighbour[0], district)
    
# Returns the neighbours of a point on the surface based on walkability
def get_neighbours(point : ivec3, world_slice : WorldSlice) -> list[ivec3]:
    neighbours = []
    height_map = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']
    
    for direction in cardinal:
        delta = vector(direction)
        neighbour = point + delta

        if neighbour.x < 0 or neighbour.z < 0 or neighbour.x >= len(height_map) or neighbour.z >= len(height_map[0]):
            # out of bounds
            continue

        neighbour.y = height_map[neighbour.x][neighbour.z]
        if abs(point.y - neighbour.y) > 1:
            neighbours.append([neighbour, point.y - neighbour.y])
        else:
            neighbours.append([neighbour, 0])

    return neighbours
    
def spawn_districts(seed : int, build_rect : Rect, world_slice : WorldSlice) -> list[District]:

    rects = []

    for i in range(int(build_rect.size.x / CHUNK_SIZE) * int(build_rect.size.y / CHUNK_SIZE)):
        rect = Rect(
            offset = ivec2(
                x = int((i // CHUNK_SIZE) * CHUNK_SIZE),
                y = int((i % CHUNK_SIZE) * CHUNK_SIZE),
            ),
            size = ivec2(
                x = int(CHUNK_SIZE),
                y = int(CHUNK_SIZE),
            )
        )
        rects.append(rect)

    rng = RNG(seed, 'get_origins')

    points = generate_district_points(rng, rects, world_slice)

    return [District(origin=pt, is_urban=False) for pt in points]

def generate_district_points(rng : RNG, rect: list[Rect], world_slice : WorldSlice) -> list[ivec3]:
    points = []
    
    for i in range(len(rect)):
        trials = 0

        while True:
            trials += 1

            if trials > RETRIES:
                print(f'Failed to place inner point {i}, retries exceeded')
                break

            x = rng.randint(int(rect[i].size.x)) + rect[i].offset.x
            z = rng.randint(int(rect[i].size.y)) + rect[i].offset.y

            trial_point = ivec3(
                x,
                world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z],
                z,
            )

            if all(distance(other_point, trial_point) >= INNER_POINTS_MIN_DISTANCE for other_point in points):
                points.append(trial_point) # success!
                break
    
    return points

def generate_inner_district_points(inner_district_num : int, rng : RNG, inner_rect: Rect, world_slice : WorldSlice) -> list[ivec3]:
    points = []
    
    for i in range(inner_district_num):
        trials = 0

        while True:
            trials += 1

            if trials > RETRIES:
                print(f'Failed to place inner point {i}, retries exceeded')
                break

            x = rng.randint(int(inner_rect.size.x)) + inner_rect.offset.x
            z = rng.randint(int(inner_rect.size.y)) + inner_rect.offset.y

            trial_point = ivec3(
                x,
                world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z],
                z,
            )

            if all(distance(other_point, trial_point) >= INNER_POINTS_MIN_DISTANCE for other_point in points):
                points.append(trial_point) # success!
                break
    
    return points

def generate_outer_district_points(outer_district_num : int, rng : RNG, build_rect: Rect, outer_ratio : float, inner_rect : Rect, world_slice : WorldSlice) -> list[ivec3]:
    points = []
    
    for i in range(outer_district_num):
        trials = 0

        while True:
            trials += 1

            if trials > RETRIES * 3:
                print(f'Failed to place outer point {i}, retries exceeded')
                break

            x = rng.randint(int(build_rect.size.x))
            z = rng.randint(int(build_rect.size.y))

            trial_point = ivec3(
                x,
                world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z],
                z
            )

            if inner_rect.contains(trial_point):
                continue

            if all(distance(other_point, trial_point) >= OUTER_POINTS_MIN_DISTANCE for other_point in points):
                points.append(trial_point) # success!
                break
    
    return points

def prune_urban_chokepoints(districts : list[District]):
    urban_count = sum(1 if district.is_urban else 0 for district in districts)

    if urban_count < 4:
        return

    for district in districts:
        if not district.is_urban:
            continue

        urban_adjacency = 0
        
        for other, value in district.adjacency.items():
            other : District
            if other.is_urban:
                urban_adjacency += value
        
        if urban_adjacency < CHOKEPOINT_ADJACENCY_RATIO * district.adjacencies_total:
            district.is_urban = False
            urban_count -= 1
            return prune_urban_chokepoints(districts)