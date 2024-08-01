from gdpc.vector_tools import ivec2, ivec3
from ...structures.legacy_directions import CARDINAL, get_ivec2, vector


def find_edges_2D(points: set[ivec2]) -> set[ivec2]:
    return {
        point
        for point in points
        if any((point + get_ivec2(direction)) not in points for direction in CARDINAL)
    }


def find_edges_3D(points: set[ivec3]) -> set[ivec3]:
    return {
        point
        for point in points
        if any((point + vector(direction)) not in points for direction in CARDINAL)
    }


# Returns outer and inner points of a set of points, where the outer points are determined by some given distance to the edge
def find_outer_and_inner_points(
    points: set[ivec2], distance: int
) -> tuple[set[ivec2], set[ivec2]]:

    edges: set[ivec2] = find_edges_2D(points)
    queue: list[tuple[ivec2, int]] = [(edge, 0) for edge in edges]
    visited: set[ivec2] = edges.copy()

    while queue:
        point, edge_distance = queue.pop(0)

        if edge_distance >= distance:
            continue

        for direction in CARDINAL:
            neighbour = point + get_ivec2(direction)

            if neighbour not in points:
                continue

            if neighbour in visited:
                continue

            visited.add(neighbour)

            queue.append((neighbour, edge_distance + 1))
            edges.add(neighbour)

    return edges, (points - edges)
