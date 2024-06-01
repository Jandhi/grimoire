from gdpc import Editor
from gdpc.vector_tools import distance, ivec3

from grimoire.districts.district import District

from ..core.maps import Map
from ..core.structures.legacy_directions import ALL_8, vector
from ..core.utils.bounds import is_in_bounds
from ..paths.a_star import COUNTER_LIMIT_EXCEEDED, a_star

HEURISTIC_WEIGHT = 3


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


def route_highway(start: ivec3, end: ivec3, map: Map, editor: Editor, is_debug=False):
    end = ivec3(*end)  # copy end

    if end.x % 4 != start.x % 4:
        end.x = (end.x - end.x % 4) + start.x % 4

    if end.z % 4 != start.z % 4:
        end.z = (end.z - end.z % 4) + start.z % 4

    end.y = map.height[end.x][end.z]

    def get_cost(prev_cost: float, path: list[ivec3]) -> float:
        if len(path) == 1:
            return 2 * distance(path[-1], end)

        last: ivec3 = path[-1]

        prev_heuristic: float = HEURISTIC_WEIGHT * distance(path[-2], end)

        path_cost: float = prev_cost - prev_heuristic
        base_length_cost = 2  # added as length of path increases

        height_diff: int = abs(last.y - map.height[last.x][last.z])
        height_cost: int = height_diff * 5

        district_cost = 0
        district_at_last: District | None = map.districts[last.x][last.z]
        if district_at_last is not None and district_at_last.is_urban:
            district_cost += 50

        near_wall_cost = 0
        # if map.near_wall and map.near_wall[last.x][last.z]:
        #    near_wall_cost += 10

        if map.water[last.x][last.z]:
            base_length_cost += 30  # WATER COST. Making this big means water gets avoided when possible.

        y_diff_penalty: int = abs(path[-1].y - path[-2].y) * 2

        return (
            path_cost
            + height_cost
            + base_length_cost
            + y_diff_penalty
            + distance(path[-2], last)
            + HEURISTIC_WEIGHT * distance(last, end)
            + district_cost
            + near_wall_cost
        )

    # prefer 4 out neighbours, but will accept 2 out
    def get_neighbours(point: ivec3) -> list[ivec3]:
        neighbours: list[ivec3] = []

        for direction in ALL_8:
            direction_vector: ivec3 = vector(direction)

            # First consider 4 out
            neighbour: ivec3 = point + direction_vector * 4

            if is_in_bounds(neighbour, map.world):
                actual_neighbour_y = map.height[neighbour.x][neighbour.z]

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

            if is_in_bounds(neighbour, map.world):
                neighbour.y = map.height[neighbour.x][neighbour.z]

                if abs(point.y - neighbour.y) <= 2:
                    neighbours.append(neighbour)
                    continue

        return neighbours

    highway: list[ivec3] | None | str = None

    if is_debug:
        highway = a_star(start, end, get_neighbours, get_cost, editor)
    else:
        highway = a_star(start, end, get_neighbours, get_cost)

    if highway == COUNTER_LIMIT_EXCEEDED:
        print("Pathfinding took too long: Trying to route to the midpoint")
        midpoint: ivec3 = (start + end) / 2

        part1: list[ivec3] | None | str = a_star(
            start, midpoint, get_neighbours, get_cost
        )
        part2: list[ivec3] | None | str = a_star(
            midpoint, end, get_neighbours, get_cost
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
        return part1 + part2

    return highway
