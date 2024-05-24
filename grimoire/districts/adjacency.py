import itertools

from gdpc import WorldSlice
from gdpc.vector_tools import Box, Rect, ivec2, ivec3

from ..core.maps import Map
from ..core.structures.legacy_directions import cardinal, vector
from ..districts.district import District


# Tells the districts what neighbours they have and why
def establish_adjacency(
    world_slice: WorldSlice, district_map: list[list[District]], map: Map
) -> None:
    build_box: Box = world_slice.box
    rect = Rect(
        (0, 0), (build_box.size.x, build_box.size.z)
    )  # rect of build area, with (0, 0) as corner

    for x, z in itertools.product(range(rect.size.x), range(rect.size.y)):
        # Don't consider unclaimed territory
        if district_map[x][z] is None:
            continue

        district: District = district_map[x][z]
        y: int = map.height_no_tree[x][z]

        if x == 0 or z == 0:  # label edge districts as non-urban
            district.is_urban = False

        for point in (ivec2(x + 1, z), ivec2(x, z + 1)):
            if not rect.contains(point):  # out of bounds
                district.is_urban = False
                continue

            point_height: int = map.height_no_tree[x][z]

            if abs(y - point_height) > 1:  # impassable, not neighbours
                continue

            point_district: District = district_map[point.x][point.y]

            # they are neighbours
            if point_district == district:  # same districts, uninteresting
                continue

            if point_district is None:
                district.adjacencies_total += 1  # log an empty adjacency
                continue

            district._add_adjacency(point_district)
            point_district._add_adjacency(district)

    find_edges(world_slice, district_map, map)


def find_edges(
    world_slice: WorldSlice, district_map: list[list[District]], city_map: Map
) -> None:
    build_box: Box = world_slice.box
    rect = Rect(
        (0, 0), (build_box.size.x, build_box.size.z)
    )  # rect of build area, with (0, 0) as corner

    for x, z in itertools.product(range(rect.size.x), range(rect.size.y)):
        y: int = city_map.height_no_tree[x][z]
        point = ivec3(x, y, z)
        district: District = district_map[x][z]

        if district is None:
            continue

        for direction in cardinal:
            neighbour: ivec3 = point + vector(direction)

            if (
                neighbour.x < 0
                or neighbour.z < 0
                or neighbour.x >= rect.size.x
                or neighbour.z >= rect.size.y
            ):
                district.edges.add(point)
            elif district_map[neighbour.x][neighbour.z] != district:
                district.edges.add(point)
