import itertools
from logging import error, warn
from typing import Generator

from gdpc import Block, Editor
from gdpc.vector_tools import CARDINALS_2D, Rect, distance2, ivec2, ivec3, neighbors2D

from grimoire.core.styling.palette import BuildStyle
from grimoire.core.utils.misc import to_list_or_none
from grimoire.placement.nooks.functions import (
    choose_suitable_nook,
    discover_nook,
    edge_to_pattern,
    find_suitable_nooks,
    identify_traffic_exposure_from_edging_pattern,
    map_developments_at_edge,
)
from grimoire.placement.nooks.nook import Nook, TrafficExposureType

from ..core.maps import DevelopmentType, Map
from ..core.noise.rng import RNG
from ..core.structures.legacy_directions import to_text
from ..core.utils.bounds import is_in_bounds2d
from ..core.utils.sets.find_outer_points import find_outer_and_inner_points
from ..core.utils.sets.set_operations import find_edges, find_outer_direction
from ..core.utils.shapes import Shape2D
from ..core.utils.vectors import point_3d, y_ivec3
from ..districts.district import DistrictType, SuperDistrict
from ..districts.district_painter import replace_ground_smooth
from ..districts.paint_palette import PaintPalette
from ..paths.lantern import place_lanterns
from ..placement.building_placement import attempt_place_building

EDGE_THICKNESS = 1
DESIRED_BLOCK_SIZE = 500  # 120
MINIMUM_BLOCK_SZE = 100  # 100


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

        if build_map.water_depth_at(vec) > 3:  # allow depth
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

        attempt_place_building(editor, edge, build_map, build_dir, rng, style)


def add_city_blocks(
    editor: Editor,
    super_districts: list[SuperDistrict],
    build_map: Map,
    seed: int,
    style=BuildStyle.JAPANESE,
    is_debug=False,
) -> tuple[list[set[ivec2]], list[set[ivec2]], list[set[ivec2]]]:
    rng = RNG(seed, "add_city_blocks")

    urban_area: set[ivec2] = set()
    for district in super_districts:
        if district.type == DistrictType.URBAN:
            urban_area |= district.points_2d

    outer_urban_area, inner_urban_area = find_outer_and_inner_points(urban_area, 3)

    for point in outer_urban_area:
        build_map.buildings[point.x][point.y] = DevelopmentType.CITY_WALL

    bubbles = generate_bubbles(rng, super_districts, build_map)
    blocks, block_map = merge_small_blocks(*bubble_out(bubbles, build_map))

    inners: list[set[ivec2]] = []
    outers = []

    for i, block in enumerate(blocks):
        if len(block) < MINIMUM_BLOCK_SZE:
            continue

        outer, inner = find_outer_and_inner_points(block, EDGE_THICKNESS)

        for point in outer:
            build_map.buildings[point.x][point.y] = DevelopmentType.CITY_ROAD

        if is_debug:
            for point in outer | outer_urban_area:
                editor.placeBlock(
                    ivec3(
                        point.x,
                        build_map.world.heightmaps["MOTION_BLOCKING_NO_LEAVES"][
                            point.x
                        ][point.y]
                        - 1,
                        point.y,
                    ),
                    Block("cobblestone"),
                )

        block_rng = RNG(seed, f"block {i}")
        inners.append(inner)
        outers.append(outer)

    city_roads = set()

    for outer in outers:
        city_roads |= outer

    urban_road: PaintPalette = (
        PaintPalette.find("desert_road")
        if style == BuildStyle.DESERT
        else PaintPalette.find("urban_road")
    )

    replace_ground_smooth(list(city_roads), urban_road.palette, rng, build_map, editor)

    # Has to be done after all inners are found
    for block, inner, outer in zip(blocks, inners, outers):
        print("New city block...")
        print("\tPlacing buildings...")
        place_buildings(editor, inner, build_map, block_rng, style, is_debug)
        print("\tDecorating...")
        decorate_city_block(editor, build_map, block, inner, outer, block_rng, style)

    place_lanterns(editor, city_roads, build_map, rng)

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
            traffic_exposure: TrafficExposureType = (
                identify_traffic_exposure_from_edging_pattern(pattern)
            )
            nook: Nook = choose_suitable_nook(
                block_rng,
                district_types=DistrictType.URBAN,
                traffic_exposure_types=traffic_exposure,
                styles=style,
                area=nook_shape,
            )
            nook.manifest(
                editor, nook_shape, surrounding_developments, city_map, block_rng
            )
            print(
                f"\t\tIt became a Nook ({nook.name}) with the following properties:\n"
                f"\t\t\t- District Type: {[t.name for t in to_list_or_none(nook.district_types)] if nook.district_types else 'Any'} ({DistrictType.URBAN.name})\n"
                f"\t\t\t- Exposure Type: {[t.name for t in to_list_or_none(nook.traffic_exposure_types)] if nook.traffic_exposure_types else 'Any'} ({traffic_exposure.name})\n"
                f"\t\t\t- Style: {[t.name for t in to_list_or_none(nook.styles)] if nook.styles else 'Any'} ({style.name})\n"
                f"\t\t\t- Area {nook.min_area}-{nook.max_area} ({len(nook_shape)})"
            )
