from typing import Callable

from gdpc import Block, Editor, WorldSlice
from gdpc.vector_tools import (
    ivec2,
    ivec3,
    addY,
    dropY,
    distance,
    CARDINALS,
    CARDINALS_2D,
    CARDINALS_AND_DIAGONALS,
    CARDINALS_AND_DIAGONALS_2D,
)

from .bridge import BridgeBuilder
from .routing import Path
from ..core.maps import Map
from ..core.structures.legacy_directions import CARDINAL, get_ivec2, to_text
from ..core.styling.blockform import BlockForm
from ..core.styling.materials.gradient import Gradient, GradientAxis, PerlinSettings
from ..core.styling.materials.material import MaterialFeature
from ..core.styling.materials.painter import PalettePainter, Painter
from ..core.styling.materials.placer import Placer
from ..core.styling.materials.traversal import MaterialTraversalStrategy
from ..core.styling.palette import BuildStyle, Palette, MaterialRole
from ..core.utils.bounds import is_in_bounds2d
from grimoire.districts.district import DistrictType
from ..core.utils.geometry import get_surrounding_points
from ..core.utils.remap import remap_threshold_high
from ..core.utils.vectors import y_ivec3

colors: list[str] = [
    "white",
    "orange",
    "magenta",
    "light_blue",
    "yellow",
    "lime",
    "pink",
    "gray",
    "light_gray",
    "cyan",
    "purple",
    "blue",
    "brown",
    "green",
    "red",
    "black",
]


def build_paths(
    paths: list[Path],
    editor: Editor,
    map: Map,
    palette: Palette,
    material_role: MaterialRole = MaterialRole.SECONDARY_STONE,
    debug: bool = False,
):

    land_segments: list[list[ivec3]] = []
    bridge_segments: list[list[ivec3]] = []
    paths_by_point: dict[ivec2, list[Path]] = {}

    for path in paths:
        for point in path.points:
            if dropY(point) not in paths_by_point:
                paths_by_point[dropY(point)] = []

            paths_by_point[dropY(point)].append(path)

        new_land_segments, new_bridge_segments = get_segments(path.points, map)
        land_segments += new_land_segments
        bridge_segments += new_bridge_segments

    land_segments_sum = []
    bridges = []
    for land_segment in land_segments:
        land_segments_sum += land_segment

        # Build land segments first
    for bridge_segment in bridge_segments:
        if distance(bridge_segment[0], bridge_segment[-1]) < 8:
            land_segments_sum += bridge_segment
        else:
            bridges.append(bridge_segment)

    build_all_land_segments(land_segments_sum, paths_by_point, editor, map)

    for bridge_segment in bridges:
        build_bridge_segment(
            bridge_segment,
            editor,
            map,
            palette,
            material_role=material_role,
        )

    if debug:
        for point in land_segments_sum:
            path = get_highest_priority_path(paths_by_point[dropY(point)])

            editor.placeBlock(
                point + y_ivec3(30),
                Block("minecraft:{}_wool".format(colors[path.priority % len(colors)])),
            )
        for segment in bridge_segments:
            for point in segment:
                editor.placeBlock(point + y_ivec3(30), Block("minecraft:cyan_wool"))


# Returns a list of land segments and bridge segments respectively
def get_segments(
    points: list[ivec3],
    build_map: Map,
) -> tuple[list[list[ivec3]], list[list[ivec3]]]:
    land_segments: list[list[ivec3]] = []
    bridge_segments: list[list[ivec3]] = []

    last_segment = []
    last_segment_is_bridge = False

    for point in points:
        if build_map.water_at(dropY(point)):
            if not last_segment_is_bridge and last_segment:
                land_segments.append(last_segment)
                last_segment = [last_segment[-1]]

            last_segment.append(point)
            last_segment_is_bridge = True
        else:
            if last_segment_is_bridge:
                last_segment.append(point)
                bridge_segments.append(last_segment)
                last_segment = []

            last_segment.append(point)
            last_segment_is_bridge = False

    if last_segment:
        if last_segment_is_bridge:
            bridge_segments.append(last_segment)
        else:
            land_segments.append(last_segment)

    return land_segments, bridge_segments


def build_bridge_segment(
    points: list[ivec3],
    editor: Editor,
    build_map: Map,
    palette: Palette,
    material_role: MaterialRole = MaterialRole.SECONDARY_STONE,
):
    print("Building bridge from {} to {}".format(points[0], points[-1]))

    length = distance(points[0], points[-1])
    thickness = 1

    if length > 10:
        thickness = 2
    if length > 25:
        thickness = 3

    BridgeBuilder(
        None,
        editor,
        build_map,
        palette,
        points[0],
        points[-1],
        max(1, length**0.5 / 2),
        4,
        thickness,
        25,
        True,
    ).run()


def build_all_land_segments(
    points: list[ivec3],
    paths_by_point: dict[ivec2, list[Path]],
    editor: Editor,
    build_map: Map,
):
    points_2d = [dropY(point) for point in points]
    point_heights = {dropY(point): point.y for point in points}

    for point in points:
        points_2d.append(dropY(point))
        point_heights[dropY(point)] = point.y

        path = get_highest_priority_path(paths_by_point[dropY(point)])

        for neighbour in get_surrounding_points({dropY(point)}, (path.width // 2)):
            if not build_map.is_in_bounds2d(neighbour):
                continue

            if neighbour in point_heights:
                paths_by_point[neighbour].append(path)
                continue

            if neighbour not in paths_by_point:
                paths_by_point[neighbour] = []

            paths_by_point[neighbour].append(path)

            points_2d.append(neighbour)
            point_heights[neighbour] = (
                point.y
            )  # TODO: This should probably be calculated better by the closest road points

    # first smooth pass
    for point in points_2d:
        y = point_heights[point]

        neighbour_y = 0
        n = 0

        for direction in CARDINALS_2D:
            neighbour = point + direction

            if neighbour not in point_heights:
                continue

            neighbour_y += point_heights[neighbour]
            n += 1

        if n == 0:
            continue

        point_heights[point] = int((y + neighbour_y) // (n + 1))

    # get rid of stragglers (all neighbours are lower or higher)
    for point in points_2d:
        if all(direction + point not in point_heights for direction in CARDINALS_2D):
            continue
        if all(
            direction + point not in point_heights
            or point_heights[direction + point] < point_heights[point]
            for direction in CARDINALS_2D
        ):
            point_heights[point] -= 1
        elif all(
            direction + point not in point_heights
            or point_heights[direction + point] > point_heights[point]
            for direction in CARDINALS_2D
        ):
            point_heights[point] += 1

    moisture_func = remap_threshold_high(
        Gradient(13, build_map, 0.6, PerlinSettings(20, 8, 2)).to_func(),
        0.3,
    )
    wear_func = remap_threshold_high(
        Gradient(17, build_map, 0.8, PerlinSettings(40, 8, 2)).to_func(),
        0.3,
    )

    # raise slabs where needed
    for point in points_2d:
        y = point_heights[point]

        higher_count = 0
        lower_count = 0

        for direction in CARDINALS_2D:
            neighbour = point + direction

            if neighbour not in point_heights:
                continue

            if point_heights[neighbour] == y + 1:
                higher_count += 1
            elif point_heights[neighbour] == y - 1:
                lower_count += 1

        if higher_count > 0 and lower_count == 0:
            y += 0.5
        if lower_count > 0 and higher_count == 0:
            y -= 0.5

        point_heights[point] = y

    # smoothing
    for point in points_2d:
        y = point_heights[point]

        diffs = {
            -1: 0,
            -0.5: 0,
            0: 0,
            0.5: 0,
            1: 0,
        }

        for direction in CARDINALS_2D:
            neighbour = point + direction

            if neighbour not in point_heights:
                continue

            diff = point_heights[neighbour] - y

            if diff not in diffs:
                continue

            diffs[diff] += 1

        if (
            y - int(y) == 0.5
            and diffs[0.5] > diffs[0]
            and diffs[-1] == 0
            and diffs[-0.5] == 0
        ):
            point_heights[point] = int(y + 1)

        if (
            y - int(y) == 0.5
            and diffs[-0.5] > diffs[0]
            and diffs[1] == 0
            and diffs[0.5] == 0
        ):
            point_heights[point] = int(y)

        if (
            y - int(y) == 0
            and diffs[0.5] > diffs[0]
            and diffs[-1] == 0
            and diffs[-0.5] == 0
        ):
            point_heights[point] = y + 0.5

        if (
            y - int(y) == 0
            and diffs[-0.5] > diffs[0]
            and diffs[1] == 0
            and diffs[0.5] == 0
        ):
            point_heights[point] = y - 0.5

    edges: dict[ivec2, int] = {}

    # building
    for point in points_2d:
        y = point_heights[point]
        x, z = point

        form = BlockForm.BLOCK

        if y - int(y) == 0.5:
            form = BlockForm.SLAB
            y += 0.5

        path = get_highest_priority_path(paths_by_point[point])

        for direction in CARDINALS_AND_DIAGONALS_2D:
            neighbour: ivec2 = point + direction

            if not build_map.is_in_bounds2d(neighbour):
                continue

            if neighbour in points_2d:
                continue

            if neighbour in edges and edges[neighbour] > y:
                continue

            edges[neighbour] = y

            if neighbour not in paths_by_point:
                paths_by_point[neighbour] = []
            paths_by_point[neighbour].append(path)

        painter = (
            Painter(editor, path.material)
            .with_feature(
                MaterialFeature.WEAR, wear_func, MaterialTraversalStrategy.SCALED
            )
            .with_feature(
                MaterialFeature.MOISTURE,
                moisture_func,
                MaterialTraversalStrategy.SCALED,
            )
        )
        painter.place_block(addY(point, y - 1), form, states={})

        if build_map.height_at(point) > y - 1:
            for dy in range(4):
                editor.placeBlock((x, y + dy, z), Block("air"))
        elif build_map.height_at(point) < y - 1:
            if int(y - 1) - build_map.height_at(point) > 5:
                for i in range(int(y - 4), int(y - 1)):
                    editor.placeBlock((x, i, z), Block("minecraft:stone"))

            for i in range(build_map.height_at(point), int(y - 1)):
                # foundation
                # TODO: Change for the biome
                editor.placeBlock((x, i, z), Block("minecraft:stone"))

    valid_edges: dict[ivec2, int] = {}

    for edge in edges:
        y = edges[edge]

        if build_map.height_at(edge) > y:
            continue

        path = get_highest_priority_path(paths_by_point[edge])

        if not path.fence:
            continue

        if build_map.height_at(edge) == y:
            valid_edges[edge] = y

    # We only want multi-fence areas
    valid_edges = {
        edge: y
        for edge, y in valid_edges.items()
        if any(direction + edge in valid_edges for direction in CARDINALS_2D)
    }

    for edge in valid_edges:
        y = edges[edge]
        path = get_highest_priority_path(paths_by_point[edge])
        painter = Painter(editor, path.fence)
        painter.place_block(addY(edge, y), BlockForm.FENCE, states={})


def get_highest_priority_path(paths: list[Path]) -> Path:
    highest_priority = None
    highest_priority_path = None

    for path in paths:
        if not highest_priority_path or path.priority > highest_priority:
            highest_priority = path.priority
            highest_priority_path = path

    return highest_priority_path
