import itertools

from districts.district import District
from gdpc import Block, Editor, WorldSlice
from gdpc.vector_tools import Rect, ivec2, ivec3
from terrain.set_height import set_height

from grimoire.core.utils.bounds import is_in_bounds2d

DISTRICT_AVG_RATIO = (
    0.5  # the percent of the height that the district average should influence
)
EDGE_RANGE = 5  # how far in both directions the edges are smoothed


def smooth_edges(
    build_rect: Rect,
    districts: list[District],
    district_map: list[list[District]],
    world_slice: WorldSlice,
    editor: Editor,
    water_map: list[list[bool]],
):
    print("Smoothing edges")

    points = set()

    for district in districts:
        if not district.is_urban:  # only need to smooth edges for urban areas
            continue

        for edge in district.edges:
            for dx, dz in itertools.product(
                range(-EDGE_RANGE, EDGE_RANGE), range(-EDGE_RANGE, EDGE_RANGE)
            ):
                pt = ivec2(edge.x + dx, edge.z + dz)

                # out of bounds
                if (
                    pt.x < 0
                    or pt.y < 0
                    or pt.x >= world_slice.box.size.x
                    or pt.y >= world_slice.box.size.z
                ):
                    continue

                # don't smooth water tiles
                if water_map[pt.x][pt.y]:
                    continue

                if pt not in points:
                    points.add(pt)

    updated_heights = {}

    for x, z in points:
        key = x, z

        updated_heights[key] = average_neighbour_height(x, z, world_slice)

    for key, y in updated_heights.items():
        x, z = key
        set_height(x, y, z, world_slice, editor)

    editor.flushBuffer()  # this is needed to reload the world slice properly
    print("Reloading worldSlice")
    world_slice = editor.loadWorldSlice(build_rect)

    for district in districts:
        update_district_points(district, world_slice)


def smooth(
    district: District,
    district_map: list[list[District]],
    world_slice: WorldSlice,
    editor: Editor,
    water_map: list[list[bool]],
):
    print(f"Smoothing {district}")
    updated_heights = {}

    for x, _, z in district.points:
        key = x, z

        # we don't want to flatten water tiles
        if water_map[x][z]:
            continue

        updated_heights[key] = average_neighbour_height(x, z, world_slice)

    for key, y in updated_heights.items():
        x, z = key
        set_height(x, y, z, world_slice, editor)


RANGE = 10
NEIGHBOURS = [
    (x, z) for x in range(-RANGE, RANGE + 1) for z in range(-RANGE, RANGE + 1)
]


def average_neighbour_height(x: int, z: int, world_slice: WorldSlice) -> int:
    height_sum: float = 0
    total_weight: float = 0

    for dx, dz in NEIGHBOURS:
        if not is_in_bounds2d(ivec2(x + dx, z + dz), world_slice):
            continue

        distance = abs(dx) + abs(dz)
        weight = 0.8**distance
        height = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][x + dx][z + dz]
        height_sum += height * weight
        total_weight += weight

    return round(height_sum / total_weight)


# updates the points set of a district to be correct
def update_district_points(district: District, world_slice: WorldSlice):
    district.points.clear()
    sum_point = ivec3(0, 0, 0)  # FIXME: Unused variable

    for x, z in district.points_2d:
        y = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][x][z]
        point = ivec3(x, y, z)
        district.points.add(point)
        sum_point += point
