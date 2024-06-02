from gdpc import WorldSlice
from gdpc.vector_tools import Rect, distance, ivec2, ivec3

from ..core.maps import Map
from ..core.noise.rng import RNG
from ..core.structures.legacy_directions import cardinal, vector
from .adjacency import establish_adjacency
from .district import District, SuperDistrict
from .district_analyze import district_analyze
from .merging_districts import merge_down

# from districts.adjacency import establish_adjacency, get_neighbours
CHUNK_SIZE = 16
TARGET_POINTS_GENERATED = 36
TARGET_DISTRICT_AMT = 16
OUTER_POINTS_MIN_DISTANCE = 10
INNER_POINTS_MIN_DISTANCE = 5
RETRIES = 100
INNER_DISTRICTS_AMOUNT_RATIO = 0.5
INNER_DISTRICTS_TARGET_AREA = 0.3  # The ratio of area where inner districts spawn
CHOKEPOINT_ADJACENCY_RATIO = 0.3  # If this percent or less of an urban district touches other urban district, it is pruned


def generate_districts(seed: int, build_rect: Rect, world_slice: WorldSlice, map: Map):
    districts = spawn_districts(seed, build_rect, map)
    district_map: list[list[District]] = [
        [None for _ in range(build_rect.size.y)] for _ in range(build_rect.size.x)
    ]

    for district in districts:
        origin = district.origin
        district_map[origin.x][origin.z] = district

    bubble_out(districts, district_map, map)

    for _ in range(2):
        district_map = [
            [None for _ in range(build_rect.size.y)] for _ in range(build_rect.size.x)
        ]
        recalculate_center_point(world_slice, districts, district_map)

        bubble_out(districts, district_map, map)

    establish_adjacency(world_slice, district_map, map)
    super_districts: list[SuperDistrict] = []
    super_district_map: list[list[District]] = [
        [None for _ in range(build_rect.size.y)] for _ in range(build_rect.size.x)
    ]
    for district in districts:
        district_analyze(district, map)
        # create a super_district parent for it
        super_district = SuperDistrict(district)
        super_districts.append(super_district)
    for super_district in super_districts:
        for point in super_district.points_2d:
            super_district_map[point.x][point.y] = super_district
    establish_adjacency(world_slice, super_district_map, map)
    merge_down(super_districts, super_district_map, TARGET_DISTRICT_AMT, map)

    # remeasure adjacency after
    for district in super_districts:
        district.adjacency = {}
        district.adjacencies_total = 0
        district.edges = set()
    establish_adjacency(world_slice, super_district_map, map)

    prune_urban_chokepoints(districts)

    return (districts, district_map, super_districts, super_district_map)


def recalculate_center_point(
    world_slice: WorldSlice,
    districts: list[District],
    district_map: list[list[District]],
):
    print("finding center point again")

    for district in districts:
        origin = district.average()  # assumes no heigh deviation
        district._recenter(origin)
        district_map[origin.x][origin.z] = district


# TODO (eventually): change way bubble out works so that each district is guaranteed to contain blocks that most walkable to its center
# (no claiming then gradually fulfiling the claim, rather gradually fulfilling the claim before grabbing the point)
def bubble_out(districts: list[District], district_map: list[list[District]], map: Map):
    # additional value added which defines how many iterations needed to claim the block
    queue = [[district.origin, 0] for district in districts]
    water_queue = []
    visited: set[ivec3] = {district.origin for district in districts}

    def add_point_to_district(point: ivec3, district: District):
        district_map[point.x][point.z] = district
        district._add_point(point)

    # first pass normal queue
    while queue:
        next_points: list[ivec3] = queue.pop(0)
        point: ivec3 = next_points[0]
        district: District = district_map[point.x][point.z]

        if next_points[1] > 0:
            queue.append([point, next_points[1] - 1])
            continue

        for neighbour in get_neighbours(point, map, district):
            if neighbour[0] in visited:
                continue

            visited.add(neighbour[0])
            add_point_to_district(neighbour[0], district)

            if map.water[neighbour[0].x][neighbour[0].z]:
                water_queue.append(neighbour[0])
            else:
                queue.append(neighbour)

    # second pass water queue
    while water_queue:
        point = water_queue.pop(0)
        district = district_map[point.x][point.z]

        for neighbour in get_neighbours(point, map, district):
            if neighbour[0] in visited:
                continue

            visited.add(neighbour[0])
            water_queue.append(neighbour[0])
            add_point_to_district(neighbour[0], district)


# Returns the neighbours of a point on the surface based on walkability
def get_neighbours(point: ivec3, map: Map, district: District) -> list[ivec3]:
    neighbours: list[list[ivec3]] = []
    height_map: list[list[int]] = map.height_no_tree

    for direction in cardinal:
        delta: ivec3 = vector(direction)
        neighbour: ivec3 = point + delta

        if (
            neighbour.x < 0
            or neighbour.z < 0
            or neighbour.x >= len(height_map)
            or neighbour.z >= len(height_map[0])
        ):
            # out of bounds
            district.is_border = True  # set is_border to true
            continue

        neighbour.y = height_map[neighbour.x][neighbour.z]
        neighbours.append([neighbour, point.y - neighbour.y])

    return neighbours


def spawn_districts(seed: int, build_rect: Rect, map: Map) -> list[District]:

    rects: list[Rect] = []

    for i in range(
        int(build_rect.size.x / CHUNK_SIZE) * int(build_rect.size.y / CHUNK_SIZE)
    ):
        rect = Rect(
            offset=ivec2(
                x=int((i // int(build_rect.size.x / CHUNK_SIZE)) * CHUNK_SIZE),
                y=int((i % int(build_rect.size.y / CHUNK_SIZE)) * CHUNK_SIZE),
            ),
            size=ivec2(
                x=int(CHUNK_SIZE),
                y=int(CHUNK_SIZE),
            ),
        )
        rects.append(rect)

    rng = RNG(seed, "get_origins")

    points = generate_district_points(rng, rects, map)

    return [District(origin=pt) for pt in points]


def generate_district_points(rng: RNG, rect: list[Rect], city_map: Map) -> list[ivec3]:
    points: list[ivec3] = []

    for i in range(len(rect)):
        trials = 0

        while True:
            trials += 1

            if trials > RETRIES:
                print(f"Failed to place inner point {i}, retries exceeded")
                break

            x: int = rng.randint(int(rect[i].size.x)) + rect[i].offset.x
            z: int = rng.randint(int(rect[i].size.y)) + rect[i].offset.y

            trial_point = ivec3(
                x,
                city_map.height_no_tree[x][z],
                z,
            )

            if all(
                distance(other_point, trial_point) >= INNER_POINTS_MIN_DISTANCE
                for other_point in points
            ):
                points.append(trial_point)  # success!
                break

    return points


def prune_urban_chokepoints(districts: list[District]) -> None:
    urban_count: int = sum(1 if district.is_urban else 0 for district in districts)

    if urban_count < 4:
        return

    for district in districts:
        if not district.is_urban:
            continue

        urban_adjacency: int = sum(
            value for other, value in district.adjacency.items() if other.is_urban
        )
        if urban_adjacency < CHOKEPOINT_ADJACENCY_RATIO * district.adjacencies_total:
            district.is_urban = False
            urban_count -= 1
            return prune_urban_chokepoints(districts)
