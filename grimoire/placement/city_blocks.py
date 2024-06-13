import itertools
from collections import Counter
from enum import Enum, auto
from logging import error, warn
from typing import Any, Generator, Iterable

from gdpc import Block, Editor
from gdpc.vector_tools import (
    CARDINALS_2D,
    DOWN_3D,
    EAST_2D,
    Rect,
    distance2,
    ivec2,
    ivec3,
    neighbors2D,
)

from grimoire.core.styling.palette import BuildStyle
from grimoire.core.utils.misc import to_list_or_none
from grimoire.placement.nooks import (
    ExposureType,
    Nook,
    find_suitable_nooks,
    identify_exposure_type_from_edging_pattern,
)

from ..core.maps import DevelopmentType, Map
from ..core.noise.rng import RNG
from ..core.structures.legacy_directions import to_text
from ..core.utils.bounds import is_in_bounds2d
from ..core.utils.sets.find_outer_points import find_outer_and_inner_points
from ..core.utils.sets.set_operations import find_edges, find_outer_direction
from ..core.utils.shapes import Shape2D
from ..core.utils.vectors import point_3d, y_ivec3
from ..districts.district import District, DistrictType, SuperDistrict
from ..placement.building_placement import place_building

EDGE_THICKNESS = 1
DESIRED_BLOCK_SIZE = 500  # 120
MINIMUM_BLOCK_SZE = 100  # 100

LOOP_LIMIT = 16  # prevents uncontrolled loops from going on too long


def generate_bubbles(
    rng: RNG,
    super_districts: list[SuperDistrict],
    build_map: Map,
    desired_block_size=DESIRED_BLOCK_SIZE,
    minimum_point_distance=15,
) -> list[ivec2]:
    points: list[ivec2] = []

    for district in super_districts:
        if district.type != DistrictType.URBAN:
            continue

        desired_point_amount = district.area // desired_block_size
        district_points_generated = 0
        trials = 0
        max_trials = 2 * desired_point_amount
        district_points = list(district.points_2d)

        while trials < max_trials and district_points_generated < desired_point_amount:
            trials += 1
            point = rng.pop(district_points)  # choose random point in districts

            if any(
                distance2(point, other) < minimum_point_distance for other in points
            ):
                continue

            if build_map.buildings[point.x][point.y] == DevelopmentType.CITY_WALL:
                continue

            district_points_generated += 1
            points.append(point)

    return points


def bubble_out(
    bubbles: list[ivec2], build_map: Map
) -> tuple[list[set[ivec2]], list[list[int | None]], dict[int, dict[int, int]]]:
    block_index_map: list[list[int | None]] = [
        [None for _ in range(len(build_map.super_districts[0]))]
        for _ in range(len(build_map.super_districts))
    ]
    blocks: list[set[ivec2]] = [set() for _ in bubbles]
    num_blocks = len(blocks)
    block_adjacency = {
        block: {other: 0 for other in range(num_blocks)} for block in range(num_blocks)
    }

    for i, bubble in enumerate(bubbles):
        blocks[i].add(bubble)
        block_index_map[bubble.x][bubble.y] = i

    queue = list(bubbles)

    def is_eligible(vec: ivec2):
        district = build_map.super_districts[vec.x][vec.y]

        if build_map.buildings[vec.x][vec.y] == DevelopmentType.CITY_WALL:
            return False

        if build_map.water[vec.x][vec.y]:
            return False

        return district is not None and district.type == DistrictType.URBAN

    while queue:
        point = queue.pop(0)
        block_index = block_index_map[point.x][point.y]
        block: set[ivec2] = blocks[block_index]

        for direction in CARDINALS_2D:
            neighbour = point + direction

            if not is_in_bounds2d(neighbour, build_map.world):
                continue

            point_y = build_map.world.heightmaps["MOTION_BLOCKING_NO_LEAVES"][point.x][
                point.y
            ]
            neighbour_y = build_map.world.heightmaps["MOTION_BLOCKING_NO_LEAVES"][
                neighbour.x
            ][neighbour.y]

            if abs(point_y - neighbour_y) > 1:
                continue

            neighbour_block_index = block_index_map[neighbour.x][neighbour.y]
            if neighbour_block_index is not None:
                block_adjacency[block_index][neighbour_block_index] += 1
                block_adjacency[neighbour_block_index][block_index] += 1
                continue

            if not is_eligible(neighbour):
                continue

            block_index_map[neighbour.x][neighbour.y] = block_index
            block.add(neighbour)
            queue.append(neighbour)

    return blocks, block_index_map, block_adjacency


def merge_small_blocks(
    blocks: list[set[ivec2]],
    block_map: list[list[int]],
    block_adjacency: dict[int, dict[int, int]],
):
    for index, block in enumerate(blocks):
        if len(block) > MINIMUM_BLOCK_SZE:
            continue

        best_neighbour = None
        best_index = 0
        best_adjacency = -1

        for other_index, adjacency in block_adjacency[index].items():
            if adjacency > best_adjacency:
                best_neighbour = blocks[other_index]
                best_index = other_index

        # couldn't find someone to merge with
        if best_neighbour is None:
            continue

        for point in block:
            best_neighbour.add(point)
            block_map[point.x][point.y] = best_index

        block.clear()

    return blocks, block_map


def place_buildings(
    editor,
    block,
    build_map,
    rng,
    style=BuildStyle.JAPANESE,
    is_debug=False,
    stilts=False,
):
    """
    Places buildings on the map edges based on the provided parameters.

    Args:
        editor: The Editor object for placing blocks.
        block: A set of 2D vectors representing the building blocks.
        build_map: The Map object representing the game map.
        rng: The RNG object for random number generation.
        style: The style of the buildings (default is BuildStyle.JAPANESE).
        is_debug: A boolean indicating whether debug mode is enabled (default is False).
    """

    edges = find_edges(block)

    for edge in edges:
        build_dir = find_outer_direction(edge, block, rng.chance(1, 2))

        if is_debug:
            editor.placeBlock(
                point_3d(edge, build_map.world) + y_ivec3(-1),
                Block("cobblestone_stairs", {"facing": to_text(build_dir)}),
            )

        place_building(editor, edge, build_map, build_dir, rng, style, stilts=stilts)


def add_city_blocks(
    editor: Editor,
    super_districts: list[SuperDistrict],
    city_map: Map,
    seed: int,
    style=BuildStyle.JAPANESE,
    is_debug=False,
    stilts=False,
) -> tuple[list[set[ivec2]], list[set[ivec2]], list[set[ivec2]]]:
    rng = RNG(seed, "add_city_blocks")

    urban_area: set[ivec2] = set()
    for district in super_districts:
        if district.type == DistrictType.URBAN:
            urban_area |= district.points_2d

    outer_urban_area, inner_urban_area = find_outer_and_inner_points(urban_area, 3)

    for point in outer_urban_area:
        city_map.buildings[point.x][point.y] = DevelopmentType.CITY_WALL

    bubbles = generate_bubbles(rng, super_districts, city_map)
    blocks, block_map = merge_small_blocks(*bubble_out(bubbles, city_map))

    inners: list[set[ivec2]] = []
    outers = []

    for i, block in enumerate(blocks):
        if len(block) < MINIMUM_BLOCK_SZE:
            continue

        outer, inner = find_outer_and_inner_points(block, EDGE_THICKNESS)

        for point in outer:
            city_map.buildings[point.x][point.y] = DevelopmentType.CITY_ROAD

        if is_debug:
            for point in outer | outer_urban_area:
                editor.placeBlock(
                    ivec3(
                        point.x,
                        city_map.world.heightmaps["MOTION_BLOCKING_NO_LEAVES"][point.x][
                            point.y
                        ]
                        - 1,
                        point.y,
                    ),
                    Block("cobblestone"),
                )

        block_rng = RNG(seed, f"block {i}")
        inners.append(inner)
        outers.append(outer)

    # Has to be done after all inners are found
    for block, inner, outer in zip(blocks, inners, outers):
        print("New city block...")
        print("\tPlacing buildings...")
        place_buildings(editor, inner, city_map, block_rng, style, is_debug)
        print("\tDecorating...")
        decorate_city_block(editor, city_map, block, inner, outer, block_rng, style)

    return (blocks, inners, outers)


def decorate_city_block(
    editor: Editor,
    city_map: Map,
    block: set[ivec2],
    inner: set[ivec2],
    outer: set[ivec2],
    block_rng: RNG,
    style: BuildStyle,
) -> None:
    SCAN_STEP: int = 4

    inner_shape = Shape2D(inner)
    outer_shape = Shape2D(outer)
    bounds = outer_shape.to_boundry_rect()

    # the grid to be scanned for potential Nook locations
    scan_grid: Generator[ivec2, None, None] = (
        ivec2(x, y)
        for x, y in itertools.product(
            range(inner_shape.begin.x, inner_shape.end.x, SCAN_STEP),
            range(inner_shape.begin.y, inner_shape.end.y, SCAN_STEP),
        )
    )

    # scan the city block to find a nook
    for scan_position in scan_grid:
        # if an empty space is found
        if city_map.buildings[scan_position.x][scan_position.y] is None:
            print(f"\t\tFound Nook candidate at {scan_position}...")
            nook_edge, nook_shape = discover_nook(scan_position, outer_shape, city_map)
            if nook_shape.begin == nook_shape.end:
                print(f"\t\t...but it could not be expanded (consists only of edge).")
                continue
            surrounding_developments: dict[ivec2, set[DevelopmentType]] = (
                map_developments_at_edge(nook_edge, city_map, bounds)
            )
            pattern: list[tuple[set[DevelopmentType], int]] = edge_to_pattern(
                scan_position, surrounding_developments, bounds
            )
            # select an appropriate Nook type and manifest it
            exposure: ExposureType = identify_exposure_type_from_edging_pattern(pattern)
            nook: Nook = block_rng.choose(
                list(
                    find_suitable_nooks(
                        district_types=DistrictType.URBAN,
                        exposure_types=exposure,
                        styles=style,
                        area=nook_shape,
                    )
                )
            )
            nook.manifest(
                editor, nook_shape, surrounding_developments, city_map, block_rng
            )
            print(
                f"\t\tIt became a Nook ({nook.name}) with the following properties:\n"
                f"\t\t\t- District Type: {[t.name for t in to_list_or_none(nook.district_types)] if nook.district_types else 'Any'} ({DistrictType.URBAN.name})\n"
                f"\t\t\t- Exposure Type: {[t.name for t in to_list_or_none(nook.exposure_types)] if nook.exposure_types else 'Any'} ({exposure.name})\n"
                f"\t\t\t- Style: {[t.name for t in to_list_or_none(nook.styles)] if nook.styles else 'Any'} ({style.name})\n"
                f"\t\t\t- Area {nook.min_area}-{nook.max_area} ({len(nook_shape)})"
            )


def discover_nook(
    start: ivec2, city_block_shape: Shape2D, city_map: Map
) -> tuple[set[ivec2], Shape2D]:
    """Find the extent of a potential Nook in a city block, starting at a free space."""

    development_map: list[list[DevelopmentType | None]] = city_map.buildings
    valid_rect = city_block_shape.to_rect()
    bounding_rect = city_block_shape.to_boundry_rect()

    if development_map[start.x][start.y] is not None:
        raise ValueError(
            f"Start ({start}) must be unoccupied in the city map (is {development_map[start.x][start.y]})"
        )

    nook_edge: set[ivec2] = set()
    nook_area = Shape2D()

    stack: list[ivec2] = [start]
    visited: set[ivec2] = set()

    # trace the nook, returning its edge and non-edge area
    while stack:
        position = stack.pop()

        if position in visited:
            continue

        visited.add(position)

        if development_map[position.x][position.y]:
            continue

        for neighbor in neighbors2D(position, bounding_rect, diagonal=True):

            # has a developed neighbour
            if development_map[neighbor.x][neighbor.y] or not valid_rect.contains(
                neighbor
            ):
                visited.add(neighbor)
                nook_edge.add(position)

            if neighbor not in visited:
                stack.append(neighbor)

        # did not have a developed neighbour
        if position not in nook_edge:
            nook_area.add(position)

    return nook_edge, nook_area


def map_developments_at_edge(
    edge: set[ivec2], city_map: Map, bounds: Rect
) -> dict[ivec2, set[DevelopmentType]]:
    development_set: dict[ivec2, set[DevelopmentType]] = {}
    for point in edge:
        for neighbor in neighbors2D(point, bounds):
            if development := city_map.buildings[neighbor.x][neighbor.y]:
                if point not in development_set:
                    development_set[point] = set()
                development_set[point].add(development)

    return development_set


def edge_to_pattern(
    start: ivec2, edge: dict[ivec2, set[DevelopmentType]], bounds: Rect
) -> list[tuple[set[DevelopmentType], int]]:

    edge_start: ivec2 = ivec2(start)

    if not edge:
        return []

    pattern: list[tuple[set[DevelopmentType], int]] = []

    for direction in CARDINALS_2D:
        edge_start = ivec2(start)
        for _ in range(LOOP_LIMIT):
            if edge_start in edge:
                break
            edge_start += direction
        else:
            continue
        break
    else:
        raise RuntimeError(
            f"Could not find an edge to the Nook originating from {start} (intervened at {edge_start})."
        )

    for current in determine_edge_sequence(start, bounds, edge):

        if current not in edge:
            error(
                f"Current position {current} is not a valid edge value! It is being skipped."
            )
            continue

        if not pattern or edge[current] != pattern[-1][0]:  # new pattern segment
            pattern.append((edge[current], 1))
            continue
        pattern[-1] = (pattern[-1][0], pattern[-1][1] + 1)  # extend current segment

    return pattern


def determine_edge_sequence(
    start: ivec2, bounds: Rect, edge: Iterable[ivec2]
) -> Generator[ivec2, Any, None]:
    current_position: ivec2 = start
    visited: set[ivec2] = set()

    stack = [start]

    while stack:
        current_position = stack.pop()
        yield current_position
        visited.add(current_position)

        for neighbor in neighbors2D(current_position, bounds):
            if neighbor in edge and neighbor not in visited:
                stack.append(neighbor)

    return
