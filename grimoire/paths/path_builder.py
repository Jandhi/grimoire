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
)

from .bridge import BridgeBuilder
from ..core.maps import Map
from ..core.structures.legacy_directions import CARDINAL, get_ivec2, to_text
from ..core.styling.blockform import BlockForm
from ..core.styling.materials.gradient import Gradient, GradientAxis, PerlinSettings
from ..core.styling.materials.material import MaterialFeature
from ..core.styling.materials.painter import PalettePainter
from ..core.styling.materials.placer import Placer
from ..core.styling.materials.traversal import MaterialTraversalStrategy
from ..core.styling.palette import BuildStyle, Palette, MaterialRole
from ..core.utils.bounds import is_in_bounds2d
from grimoire.districts.district import DistrictType
from ..core.utils.remap import remap_threshold_high
from ..core.utils.vectors import y_ivec3


def build_highways(
    highways: list[list[ivec3]],
    editor: Editor,
    world_slice: WorldSlice,
    map: Map,
    palette: Palette,
    material_role: MaterialRole = MaterialRole.SECONDARY_STONE,
    debug: bool = False,
):
    print(highways)
    land_segments: list[list[ivec3]] = []
    bridge_segments: list[list[ivec3]] = []

    for highway in highways:
        new_land_segments, new_bridge_segments = get_segments(highway, map)
        land_segments += new_land_segments
        bridge_segments += new_bridge_segments

    land_segments_sum = []
    for land_segment in land_segments:
        land_segments_sum += land_segment

    build_all_land_segments(land_segments_sum, editor, map, palette, material_role)
    bridges = []

    # Build land segments first
    for bridge_segment in bridge_segments:
        if distance(bridge_segment[0], bridge_segment[-1]) < 8:
            build_land_segment(
                bridge_segment,
                editor,
                map,
                world_slice,
                palette,
                material_role=material_role,
            )
        else:
            bridges.append(bridge_segment)

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
            editor.placeBlock(point + y_ivec3(30), Block("minecraft:gray_wool"))
        for segment in bridge_segments:
            for point in segment:
                editor.placeBlock(point + y_ivec3(30), Block("minecraft:cyan_wool"))


def build_highway(
    points: list[ivec3],
    editor: Editor,
    world_slice: WorldSlice,
    map: Map,
    palette: Palette,
    material_role: MaterialRole = MaterialRole.SECONDARY_STONE,
):
    land_segments, bridge_segments = get_segments(points, map)

    land_segment_sum = []

    for land_segment in land_segments:
        land_segment_sum += land_segment

    build_land_segment(
        land_segment_sum,
        editor,
        map,
        world_slice,
        palette,
        material_role=material_role,
    )

    for bridge_segment in bridge_segments:
        if distance(bridge_segment[0], bridge_segment[-1]) < 10:
            build_land_segment(
                bridge_segment,
                editor,
                map,
                world_slice,
                palette,
                material_role=material_role,
            )
        else:
            build_bridge_segment(
                bridge_segment,
                editor,
                map,
                palette,
                material_role=material_role,
            )


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
    editor: Editor,
    build_map: Map,
    palette: Palette,
    material_role: MaterialRole = MaterialRole.SECONDARY_STONE,
):
    points_2d = [dropY(point) for point in points]
    point_heights = {dropY(point): point.y for point in points}

    for point in points:
        points_2d.append(dropY(point))
        point_heights[dropY(point)] = point.y

        for direction in CARDINALS_2D:
            neighbour = dropY(point) + direction

            if not build_map.is_in_bounds2d(neighbour):
                continue

            if neighbour in point_heights:
                continue

            points_2d.append(neighbour)
            point_heights[neighbour] = point.y

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
        x, z = point

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

    # building
    for point in points_2d:
        y = point_heights[point]
        x, z = point

        form = BlockForm.BLOCK

        if y - int(y) == 0.5:
            form = BlockForm.SLAB
            y += 0.5

        palette_painter = (
            PalettePainter(editor, palette)
            .with_feature(MaterialFeature.WEAR, wear_func)
            .with_feature(MaterialFeature.MOISTURE, moisture_func)
        )
        palette_painter.place_block(addY(point, y - 1), material_role, form, states={})

        if build_map.height_at(point) > y - 1:
            editor.placeBlock((x, y, z), Block("air"))
            editor.placeBlock((x, y + 1, z), Block("air"))
            editor.placeBlock((x, y + 2, z), Block("air"))
        elif build_map.height_at(point) < y - 1:
            for i in range(build_map.height_at(point), int(y - 1)):
                # foundation
                editor.placeBlock((x, i, z), Block("minecraft:stone"))


def build_land_segment(
    points: list[ivec3],
    editor: Editor,
    build_map: Map,
    world_slice: WorldSlice,
    palette: Palette,
    material_role: MaterialRole = MaterialRole.SECONDARY_STONE,
):
    master_points: set[ivec2] = set()
    counted_points: set[ivec2] = set()
    final_point_heights: dict[ivec2, int] = {}

    # We fill out the land segment
    for point in points:
        point_2d = ivec2(point.x, point.z)

        master_points.add(point_2d)
        final_point_heights[point_2d] = point.y

        for direction in CARDINALS_2D:
            neighbour = point_2d + direction

            if not is_in_bounds2d(neighbour, world_slice):
                continue

            if neighbour in counted_points or neighbour in master_points:
                continue

            counted_points.add(neighbour)
            final_point_heights[neighbour] = (
                point.y
            )  # this is an estimate of height to help the next step

    blocks: dict[ivec2, Block] = {}

    moisture_func = remap_threshold_high(
        Gradient(13, build_map, 0.6, PerlinSettings(20, 8, 2)).to_func(),
        0.3,
    )
    wear_func = remap_threshold_high(
        Gradient(17, build_map, 0.8, PerlinSettings(40, 8, 2)).to_func(),
        0.3,
    )

    def generate_params(position: ivec3) -> dict[MaterialFeature, float]:
        return {
            MaterialFeature.WEAR: wear_func(position),
            MaterialFeature.MOISTURE: moisture_func(position),
        }

    for point in final_point_heights:
        x, z = point
        y = final_point_heights[point] - 1

        # don't place in urban area
        if (
            build_map.super_districts[x][z] is not None
            and build_map.super_districts[x][z].type == DistrictType.URBAN
        ):
            continue

        blocks[point] = get_block(
            point,
            final_point_heights,
            palette,
            param_generator=generate_params,
            material_role=material_role,
        )

        build_map.paths[x][z].append(y + 1)
        editor.placeBlock((x, y, z), blocks[point])

        if build_map.height_at(point) > y:
            editor.placeBlock((x, y + 1, z), Block("air"))
            editor.placeBlock((x, y + 2, z), Block("air"))
            editor.placeBlock((x, y + 3, z), Block("air"))


def get_block(
    point: ivec2,
    final_point_heights: dict[ivec2, int],
    palette: Palette,
    param_generator: Callable[[ivec3], dict[MaterialFeature, float]],
    depth=0,
    material_role: MaterialRole = MaterialRole.SECONDARY_STONE,
) -> Block:
    y_in_dir = {}
    y = final_point_heights[point]

    if depth > 10:
        return Block(
            palette.find_block_id(
                BlockForm.BLOCK,
                material_role,
                param_generator(addY(point, y)),
                {
                    MaterialFeature.WEAR: MaterialTraversalStrategy.SCALED,
                    MaterialFeature.MOISTURE: MaterialTraversalStrategy.SCALED,
                },
            ),
        )

    for direction in CARDINAL:
        dv = get_ivec2(direction)

        if point + dv not in final_point_heights:
            continue

        if abs(final_point_heights[point + dv] - y) >= 2:
            continue

        y_in_dir[direction] = final_point_heights[point + dv]

        if point - dv not in final_point_heights:
            continue

        if (
            final_point_heights[point + dv] == y + 1
            and final_point_heights[point - dv] == y - 1
        ):
            return Block(
                palette.find_block_id(
                    BlockForm.STAIRS,
                    material_role,
                    param_generator(addY(point, y)),
                    {
                        MaterialFeature.WEAR: MaterialTraversalStrategy.SCALED,
                        MaterialFeature.MOISTURE: MaterialTraversalStrategy.SCALED,
                    },
                ),
                {"facing": to_text(direction)},
            )

    if all(y_in_dir[direction] < y for direction in y_in_dir):
        final_point_heights[point] -= 1
        return get_block(
            point, final_point_heights, palette, param_generator, depth + 1
        )

    if all(y_in_dir[direction] <= y for direction in y_in_dir) and any(
        y_in_dir[direction] < y for direction in y_in_dir
    ):
        return Block(
            palette.find_block_id(
                BlockForm.SLAB,
                material_role,
                param_generator(addY(point, y)),
                {
                    MaterialFeature.WEAR: MaterialTraversalStrategy.SCALED,
                    MaterialFeature.MOISTURE: MaterialTraversalStrategy.SCALED,
                },
            ),
        )

    return Block(
        palette.find_block_id(
            BlockForm.BLOCK,
            material_role,
            param_generator(addY(point, y)),
            {
                MaterialFeature.WEAR: MaterialTraversalStrategy.SCALED,
                MaterialFeature.MOISTURE: MaterialTraversalStrategy.SCALED,
            },
        ),
    )
