from gdpc import Block, Editor, WorldSlice
from gdpc.vector_tools import ivec2, ivec3

from ..core.maps import Map
from ..core.structures.legacy_directions import CARDINAL, get_ivec2, to_text
from ..core.styling.palette import BuildStyle
from ..core.utils.bounds import is_in_bounds2d
from grimoire.districts.district import DistrictType


def build_highway(
    points: list[ivec3],
    editor: Editor,
    world_slice: WorldSlice,
    map: Map,
    style=BuildStyle.NORMAL_MEDIEVAL,
):
    master_points: set[ivec2] = set()
    neighbour_points: set[ivec2] = set()
    final_point_heights: dict[ivec2, int] = {}
    blocks: dict[ivec2, Block] = {}

    for point in points:
        point_2d = ivec2(point.x, point.z)

        master_points.add(point_2d)
        final_point_heights[point_2d] = point.y

        for direction in CARDINAL:
            neighbour = point_2d + get_ivec2(direction)

            if not is_in_bounds2d(neighbour, world_slice):
                continue

            if neighbour in neighbour_points or neighbour in master_points:
                continue

            neighbour_points.add(neighbour)
            final_point_heights[neighbour] = (
                point.y
            )  # this is an estimate of height to help the next step

    for point in final_point_heights:
        blocks[point] = get_block(point, final_point_heights, style=style)

    for point in final_point_heights:
        x, z = point
        y = final_point_heights[point] - 1

        # don't place in urban area
        if (
            map.super_districts[x][z] is not None
            and map.super_districts[x][z].type == DistrictType.URBAN
        ):
            continue

        map.highway[x][z] = True
        editor.placeBlock((x, y, z), blocks[point])

        if world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][x][z] > y:
            editor.placeBlock((x, y + 1, z), Block("air"))
            editor.placeBlock((x, y + 2, z), Block("air"))
            editor.placeBlock((x, y + 3, z), Block("air"))


def get_block(
    point: ivec2,
    final_point_heights: dict[ivec2, int],
    depth=0,
    style=BuildStyle.NORMAL_MEDIEVAL,
) -> Block:
    y_in_dir = {}
    y = final_point_heights[point]

    if depth > 10:
        return (
            Block("sandstone") if style == BuildStyle.DESERT else Block("cobblestone")
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
                (
                    "sandstone_stairs"
                    if style == BuildStyle.DESERT
                    else "cobblestone_stairs"
                ),
                {"facing": to_text(direction)},
            )

    if all(y_in_dir[direction] < y for direction in y_in_dir):
        final_point_heights[point] -= 1
        return get_block(point, final_point_heights, depth + 1, style=style)

    if all(y_in_dir[direction] <= y for direction in y_in_dir) and any(
        y_in_dir[direction] < y for direction in y_in_dir
    ):
        return Block(
            "sandstone_slab" if style == BuildStyle.DESERT else "cobblestone_slab"
        )

    return Block("sandstone" if style == BuildStyle.DESERT else "cobblestone")
