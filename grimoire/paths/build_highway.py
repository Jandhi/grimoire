from typing import Callable

from gdpc import Block, Editor, WorldSlice
from gdpc.vector_tools import ivec2, ivec3, addY

from ..core.maps import Map
from ..core.structures.legacy_directions import CARDINAL, get_ivec2, to_text
from ..core.styling.blockform import BlockForm
from ..core.styling.materials.gradient import Gradient, GradientAxis, PerlinSettings
from ..core.styling.materials.material import MaterialFeature
from ..core.styling.materials.traversal import MaterialTraversalStrategy
from ..core.styling.palette import BuildStyle, Palette, MaterialRole
from ..core.utils.bounds import is_in_bounds2d
from grimoire.districts.district import DistrictType
from ..core.utils.remap import remap_threshold_high


def build_highway(
    points: list[ivec3],
    editor: Editor,
    world_slice: WorldSlice,
    map: Map,
    palette: Palette,
    material_role: MaterialRole = MaterialRole.SECONDARY_STONE,
):
    master_points: set[ivec2] = set()
    neighbour_points: set[ivec2] = set()
    final_point_heights: dict[ivec2, int] = {}
    blocks: dict[ivec2, Block] = {}

    moisture_func = remap_threshold_high(
        Gradient(13, map, 0.6, PerlinSettings(20, 8, 2)).to_func(),
        0.3,
    )
    wear_func = remap_threshold_high(
        Gradient(17, map, 0.8, PerlinSettings(40, 8, 2)).to_func(),
        0.3,
    )

    def generate_params(position: ivec3) -> dict[MaterialFeature, float]:
        return {
            MaterialFeature.WEAR: wear_func(position),
            MaterialFeature.MOISTURE: moisture_func(position),
        }

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
        blocks[point] = get_block(
            point,
            final_point_heights,
            palette,
            param_generator=generate_params,
            material_role=material_role,
        )

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
