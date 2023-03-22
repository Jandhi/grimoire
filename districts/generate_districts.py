from noise.rng import RNG
from districts.district import District
from gdpc.vector_tools import Rect, ivec2, distance, ivec3
from gdpc import WorldSlice
from structures.directions import cardinal, get_ivec2

TARGET_DISTRICT_AMT = 50
OUTER_POINTS_MIN_DISTANCE = 10
INNER_POINTS_MIN_DISTANCE = 5
RETRIES = 100
INNER_DISTRICTS_AMOUNT_RATIO = 0.5
INNER_DISTRICTS_TARGET_AREA = 0.3 # The ratio of area where inner districts spawn

def generate_districts(build_rect : Rect, world_slice : WorldSlice) -> tuple[list[District], list[list[District]]]:
    districts = spawn_districts(seed=7, build_rect=build_rect)
    district_map : list[list[District]] = [[None for y in range(build_rect.size.y)] for x in range(build_rect.size.x)]

    for district in districts:
        origin = district.origin
        district_map[origin.x][origin.y] = district

    bubble_out(districts, world_slice, districts, district_map)
    return (districts, district_map)

def bubble_out(build_rect : Rect, world_slice : WorldSlice, districts : list[District], district_map : list[list[District]]):
    queue = [district.origin for district in districts]
    visited = {district.origin for district in districts}

    def add_point_to_district(point : ivec2, district : District):
        district_map[neighbour.x][neighbour.y] = district
        coord = ivec3(neighbour.x, world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][neighbour.x][neighbour.y], neighbour.y)
        district.add_block(coord)

    while len(queue) > 0:
        point = queue.pop(0)
        district = district_map[point.x][point.y]

        for neighbour in get_neighbours(point, world_slice):
            if neighbour in visited:
                continue

            visited.add(neighbour)
            queue.append(neighbour)
            add_point_to_district(point, district)
    

def get_neighbours(point : ivec2, world_slice : WorldSlice) -> list[ivec2]:
    neighbours = []
    height_map = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']
    
    for direction in cardinal:
        delta = get_ivec2(direction)
        neighbour = point + delta

        if neighbour.x < 0 or neighbour.y < 0 or neighbour.x >= len(height_map) or neighbour.y >= len(height_map[0]):
            # out of bounds
            continue

        if abs(height_map[point.x][point.y] - height_map[neighbour.x][neighbour.y]) > 1:
            continue
        else:
            neighbours.append(neighbour)

    return neighbours
    

def spawn_districts(seed : int, build_rect : Rect) -> list[District]:
    districts = []

    inner_district_num = int(INNER_DISTRICTS_AMOUNT_RATIO * float(TARGET_DISTRICT_AMT))
    outer_district_num = TARGET_DISTRICT_AMT - inner_district_num

    # The inner length ratio r is the proportion of the sides of an area the inner region occupies
    # The inner district's x spans from (1 - r) / 2 * x to 1 - (1 - r) / 2 * x

    inner_ratio = INNER_DISTRICTS_TARGET_AREA ** 0.5
    outer_ratio = (1 - inner_ratio) / 2
    
    build_rect.size.x

    inner_rect = Rect(
        offset = ivec2(
            x = int(outer_ratio * build_rect.size.x),
            y = int(outer_ratio * build_rect.size.y),
        ),
        size = ivec2(
            x = int(inner_ratio * build_rect.size.x),
            y = int(inner_ratio * build_rect.size.y),
        )
    )

    print(f'Attempting to generate {inner_district_num} inner districts and {outer_district_num} outer districts')
    rng = RNG(seed, 'get_origins')

    points : list[ivec2] = []

    generate_inner_district_points(inner_district_num, rng, inner_rect, points)
    for point in points:
        districts.append(District(point, True))
    points : list[ivec2] = []
    generate_outer_district_points(outer_district_num, rng, build_rect, outer_ratio, inner_rect, points)
    for point in points:
        districts.append(District(point, False))
    return districts

def generate_inner_district_points(inner_district_num : int, rng : RNG, inner_rect: Rect, points : list[ivec2]):
    for i in range(inner_district_num):
        trials = 0

        while True:
            trials += 1

            if trials > RETRIES:
                print(f'Failed to place inner point {i}, retries exceeded')
                break

            trial_point = ivec2(
                x = rng.randint(int(inner_rect.size.x)) + inner_rect.offset.x,
                y = rng.randint(int(inner_rect.size.y)) + inner_rect.offset.y,
            )

            if all(distance(other_point, trial_point) >= INNER_POINTS_MIN_DISTANCE for other_point in points):
                points.append(trial_point) # success!
                break

def generate_outer_district_points(outer_district_num : int, rng : RNG, build_rect: Rect, outer_ratio : float, inner_rect : Rect, points : list[ivec2]):
    for i in range(outer_district_num):
        trials = 0

        while True:
            trials += 1

            if trials > RETRIES * 3:
                print(f'Failed to place outer point {i}, retries exceeded')
                break

            trial_point = ivec2(
                x = rng.randint(int(build_rect.size.x)),
                y = rng.randint(int(build_rect.size.y)),
            )

            if inner_rect.contains(trial_point):
                continue

            if all(distance(other_point, trial_point) >= OUTER_POINTS_MIN_DISTANCE for other_point in points):
                points.append(trial_point) # success!
                break