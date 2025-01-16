from typing import Callable

from gdpc import Editor
from gdpc.vector_tools import distance, ivec3, dropY

from grimoire.districts.district import District, DistrictType

from ..core.maps import Map
from ..core.structures.legacy_directions import ALL_8, vector
from ..core.utils.bounds import is_in_bounds
from ..core.utils.vectors import mod_xz
from ..paths.a_star import COUNTER_LIMIT_EXCEEDED, a_star

HEURISTIC_WEIGHT = 8


def fill_out_highway(points: list[ivec3]) -> list[ivec3]:
    point_a: ivec3 = points.pop()

    full_points: list[ivec3] = [point_a]
    while points:
        point_b: ivec3 = points.pop()

        full_points += find_in_betweeners(point_a, point_b)
        full_points.append(point_a)

        point_a = point_b

    return full_points


def find_in_betweeners(point_a: ivec3, point_b: ivec3) -> list[ivec3]:
    diff_vec = ivec3(0, 0, 0)
    magnitude = 2
    points = []

    if point_a.x + 2 == point_b.x:
        diff_vec += ivec3(1, 0, 0)
    elif point_a.x + 4 == point_b.x:
        diff_vec += ivec3(1, 0, 0)
        magnitude = 4

    if point_a.z + 2 == point_b.z:
        diff_vec += ivec3(0, 0, 1)
    elif point_a.z + 4 == point_b.z:
        diff_vec += ivec3(0, 0, 1)
        magnitude = 4

    if point_a.x - 2 == point_b.x:
        diff_vec += ivec3(-1, 0, 0)
    elif point_a.x - 4 == point_b.x:
        diff_vec += ivec3(-1, 0, 0)
        magnitude = 4

    if point_a.z - 2 == point_b.z:
        diff_vec += ivec3(0, 0, -1)
    elif point_a.z - 4 == point_b.z:
        diff_vec += ivec3(0, 0, -1)
        magnitude = 4

    for i in range(1, magnitude):
        pt = point_a + i * diff_vec

        pt.y = (point_a.y * (magnitude - i) + point_b.y * i) // magnitude

        points.append(pt)

    return points


# every point neighbours
def get_neighbours(point: ivec3, build_map) -> list[ivec3]:
    neighbours: list[ivec3] = []

    for direction in ALL_8:
        direction_vector: ivec3 = vector(direction)

        neighbour: ivec3 = point + direction_vector

        if is_in_bounds(neighbour, build_map.world):
            neighbour.y = build_map.height[neighbour.x][neighbour.z]

            if abs(point.y - neighbour.y) <= 2:
                neighbours.append(neighbour)
        else:
            print(f"neighbour {neighbour} out of bounds")

    return neighbours


# prefer 4 out neighbours, but will accept 2 out
def get_neighbours_4_out_or_2(point: ivec3, build_map) -> list[ivec3]:
    neighbours: list[ivec3] = []

    for direction in ALL_8:
        direction_vector: ivec3 = vector(direction)

        # First consider 4 out
        neighbour: ivec3 = point + direction_vector * 4

        if is_in_bounds(neighbour, build_map.world):
            actual_neighbour_y = build_map.height[neighbour.x][neighbour.z]

            if point.y < actual_neighbour_y - 2:
                neighbour.y = point.y + 2
            elif point.y > actual_neighbour_y + 2:
                neighbour.y = point.y - 2
            else:
                neighbour.y = actual_neighbour_y

            if abs(point.y - neighbour.y) <= 2:
                neighbours.append(neighbour)
                continue

        # Don't consider compounds for short jumps
        if sum(direction_vector) >= 2:
            continue

        # Then consider 2 out
        neighbour = point + direction_vector * 2

        if is_in_bounds(neighbour, build_map.world):
            neighbour.y = build_map.height[neighbour.x][neighbour.z]

            if abs(point.y - neighbour.y) <= 2:
                neighbours.append(neighbour)
                continue

    return neighbours


# Finds the nearest point that is a multiple of 4 such that the point doesn't have a huge height difference
def find_best_mod4_point(point: ivec3, build_map: Map) -> ivec3:
    for diff in ivec3(0, 0, 0), ivec3(4, 0, 0), ivec3(0, 0, 4), ivec3(4, 0, 4):
        new_point = mod_xz(point, 4) + diff

        if is_in_bounds(new_point, build_map.world):
            new_point.y = build_map.height[new_point.x][new_point.z]

            if abs(point.y - new_point.y) <= 2:
                return new_point

    # Otherwise, we just gotta run with it :/
    return mod_xz(point, 4)


def get_heuristic_point(path: list[ivec3]) -> ivec3:
    if len(path) > 4:
        return path[-4]

    return path[-len(path)]


def get_cost(prev_cost: float, path: list[ivec3], end: ivec3, build_map: Map) -> float:
    if len(path) == 1:
        return 2 * distance(path[-1], end)

    last: ivec3 = path[-1]

    prev_heuristic: float = HEURISTIC_WEIGHT * distance(
        get_heuristic_point(path[:-1]), end
    )

    path_cost: float = prev_cost - prev_heuristic
    base_length_cost = 30  # added as length of path increases
    if last.y in build_map.paths[last.x][last.z]:  # NO LENGTH COST FOR HIGHWAY
        base_length_cost -= 25

    # The cost of building above or below ground
    height_diff: int = abs(last.y - build_map.height[last.x][last.z])
    height_cost: int = height_diff * 100

    district_cost = 0
    district_at_last: District | None = build_map.districts[last.x][last.z]
    if district_at_last is not None and district_at_last.type == DistrictType.URBAN:
        district_cost += 250

    near_wall_cost = 0
    # if map.near_wall and map.near_wall[last.x][last.z]:
    #    near_wall_cost += 50

    # penalize going over water
    if build_map.water[last.x][last.z]:
        base_length_cost += (
            300  # WATER COST. Making this big means water gets avoided when possible.
        )

    # penalize the path for going up and down
    y_diff_penalty: int = abs(path[-1].y - path[-2].y) * 10

    # penalize the path for wobbling
    diffs = [path[i] - path[i - 1] for i in range(1, len(path))]
    diff_diffs = [diffs[i] - diffs[i - 1] for i in range(1, len(diffs))]
    sum_diff_diffs = sum([abs(diff.x) + abs(diff.z) for diff in diff_diffs])

    return (
        path_cost
        + height_cost
        + base_length_cost
        + y_diff_penalty
        + distance(path[-2], last)
        + HEURISTIC_WEIGHT * distance(get_heuristic_point(path), end)
        + district_cost
        + near_wall_cost
        + sum_diff_diffs
    )


def route_highway(
    start: ivec3, end: ivec3, build_map: Map, editor: Editor, is_debug=False
):
    new_start = find_best_mod4_point(start, build_map)
    new_end = find_best_mod4_point(end, build_map)
    print(f"start: {start} -> {new_start}")
    print(f"end: {end} -> {new_end}")

    def get_neighbours_direct(point: ivec3) -> list[ivec3]:
        return get_neighbours(point, build_map)

    def get_neighbours_4(point: ivec3) -> list[ivec3]:
        return get_neighbours_4_out_or_2(point, build_map)

    def get_cost_func_from_end(my_end: ivec3) -> Callable[[float, list[ivec3]], float]:
        def calculate_cost(prev_cost: float, path: list[ivec3]) -> float:
            return get_cost(prev_cost, path, my_end, build_map)

        return calculate_cost

    start_to_highway: list[ivec3] | None | str = (
        [start]
        if start == new_start
        else a_star(
            start,
            new_start,
            get_neighbours_direct,
            get_cost_func_from_end(new_start),
            editor if is_debug else None,
        )
    )

    highway: list[ivec3] | None | str = a_star(
        new_start,
        new_end,
        get_neighbours_4,
        get_cost_func_from_end(end),
        editor if is_debug else None,
    )

    highway_to_end: list[ivec3] | None | str = (
        [end]
        if end == new_end
        else a_star(
            new_end,
            end,
            get_neighbours_direct,
            get_cost_func_from_end(end),
            editor if is_debug else None,
        )
    )

    if (
        start_to_highway == COUNTER_LIMIT_EXCEEDED
        or start_to_highway is None
        or highway_to_end == COUNTER_LIMIT_EXCEEDED
        or highway_to_end is None
    ):
        return None

    if highway == COUNTER_LIMIT_EXCEEDED:
        print("Pathfinding took too long: Trying to route to the midpoint")
        midpoint: ivec3 = find_best_mod4_point((start + end) / 2, build_map)

        part1: list[ivec3] | None | str = a_star(
            new_start, midpoint, get_neighbours_4, get_cost_func_from_end(midpoint)
        )
        part2: list[ivec3] | None | str = a_star(
            midpoint, new_end, get_neighbours_4, get_cost_func_from_end(new_end)
        )

        if (
            part1 == COUNTER_LIMIT_EXCEEDED
            or part2 == COUNTER_LIMIT_EXCEEDED
            or part1 is None
            or part2 is None
        ):
            return None

        if type(part1) is not list[ivec3] or type(part2) is not list[ivec3]:
            raise RuntimeError("Failed pathfinding here too!")

        part1.pop()
        return start_to_highway + part1[1:] + part2[1:] + highway_to_end[1:]

    return start_to_highway + highway[1:] + highway_to_end[1:]
