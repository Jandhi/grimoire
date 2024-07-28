from heapq import heappop, heappush
from typing import Callable
from gdpc import Editor, Block
from glm import ivec3

from grimoire.core.utils.vectors import y_ivec3

# get_neighbours takes state
# get_cost takes prev_cost and path

COUNTER_LIMIT = 500000
COUNTER_LIMIT_EXCEEDED = "counter limit exceeded"


def a_star(
    start: ivec3,
    end: ivec3,
    get_neighbours: Callable[[ivec3], list[ivec3]],
    get_cost: Callable[[float, list[ivec3]], float],
    debug_editor: Editor | None = None,
) -> list[ivec3] | None | str:
    first_path: list[ivec3] = [start]
    paths: list[tuple[float, list[ivec3]]] = [(get_cost(0, first_path), first_path)]
    visited: set[ivec3] = set()
    counter = 0

    while paths:
        counter += 1
        if counter % 10000 == 0:
            print(f"counter at {counter}")

        if counter > COUNTER_LIMIT:
            return COUNTER_LIMIT_EXCEEDED

        curr_cost, curr_path = heappop(paths)

        endpoint: ivec3 = curr_path[-1]

        visited.add(endpoint)
        if debug_editor:
            debug_editor.placeBlock(endpoint + y_ivec3(20), Block("blue_wool"))

        for neighbour in get_neighbours(endpoint):
            if neighbour in visited:
                continue

            if neighbour == end:
                return curr_path + [neighbour]

            new_path: list[ivec3] = curr_path + [neighbour]
            cost: float = get_cost(curr_cost, new_path)

            heappush(paths, (cost, new_path))

    # no dice
    return None
