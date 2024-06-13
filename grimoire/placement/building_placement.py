import contextlib

from gdpc import Block, Editor
from gdpc.vector_tools import ivec2, ivec3, vec2

from grimoire.core.styling.legacy_palette import LegacyPalette, fix_block_name
from grimoire.core.styling.palette import BuildStyle

from ..buildings.build_floor import build_floor
from ..buildings.building_plan import BuildingPlan
from ..buildings.building_shape import BuildingShape
from ..buildings.clear_interiors import clear_interiors
from ..buildings.roofs.build_roof import build_roof
from ..buildings.roofs.roof_component import RoofComponent
from ..buildings.rooms.furnish import furnish, furnish_building
from ..buildings.stilts import build_stilt_frame
from ..buildings.walls.build_walls import build_walls
from ..buildings.walls.wall import Wall
from ..core.maps import DevelopmentType, Map
from ..core.noise.rng import RNG
from ..core.structures.grid import Grid
import grimoire.core.structures.legacy_directions as legacy_directions
from ..core.structures.legacy_directions import (
    CARDINAL,
    X_MINUS,
    X_PLUS,
    Z_MINUS,
    Z_PLUS,
    LegacyDirection,
    get_ivec2,
)
from ..core.styling.blockform import BlockForm
from ..core.styling.materials.material import MaterialParameters
from ..core.styling.palette import MaterialRole, Palette
from ..core.utils.geometry import get_surrounding_points
from ..districts.district import DistrictType

offsets = {
    Z_MINUS: [ivec2(0, 0), ivec2(-1, 0)],
    X_MINUS: [ivec2(0, 0), ivec2(0, -1)],
    X_PLUS: [ivec2(-1, -1), ivec2(-1, 0)],
    Z_PLUS: [ivec2(-1, -1), ivec2(0, -1)],
}

door_points = {
    Z_MINUS: vec2(0.5, 0),
    Z_PLUS: vec2(0.5, 1),
    X_PLUS: vec2(1, 0.5),
    X_MINUS: vec2(0, 0.5),
}

WATER_THRESHOLD = 0.4  # above this threshold a house cannot be built
MAX_AVG_HEIGHT_DIFF = 4


# Attempts to place a building at a point
# returns True on success
def place_building(
    editor: Editor,
    start_point: ivec2,
    map: Map,
    outside_direction: str,
    rng: RNG,
    style: BuildStyle = BuildStyle.JAPANESE,
    urban_only=True,
    stilts: bool = False,
) -> bool:
    # A building can always be placed with the door to the left or right of the original spot
    my_offsets = offsets[outside_direction]

    shapes: list[BuildingShape] = BuildingShape.all()

    # We increase the weight of larger buildings exponentially since they are much harder to place
    def building_shape_weight(shape: BuildingShape):
        return len(shape.points) ** 2 + 2

    weighted_shape_dict = {
        shape: building_shape_weight(shape)
        for shape in shapes
        if shape.door_direction == outside_direction
    }

    # iterate over shapes randomly by weight
    while True:
        shape: BuildingShape = rng.pop_weighted(weighted_shape_dict)

        if shape is None:
            return False

        if shape.door_direction != outside_direction:
            continue

        for offset in my_offsets:
            success = attempt_building_placement_at_offset(
                editor,
                rng,
                map,
                start_point,
                offset,
                outside_direction,
                shape,
                style,
                urban_only,
                allow_water=stilts,
                stilts=stilts,
            )

            if success:
                return True


# Attempts to place building, returns success status
def attempt_building_placement_at_offset(
    editor: Editor,
    rng: RNG,
    map: Map,
    start_point: ivec2,
    offset: ivec2,
    outside_direction: LegacyDirection,
    shape: BuildingShape,
    style: BuildStyle,
    urban_only: bool,
    allow_water: bool = False,
    stilts: bool = False,
) -> bool:
    grid = Grid()
    origin = start_point + ivec2(
        offset.x * grid.dimensions.x, offset.y * grid.dimensions.z
    )

    if stilts:
        origin += ivec2(3, 3)

    # We have to find the proper height for the door to be at ground level
    door_point = ivec2(*door_points[outside_direction])
    door_point.x = (
        (grid.dimensions.x // 2 + 1)
        if door_point.x == 0.5
        else door_point.x * (grid.dimensions.x - 1)
    )
    door_point.y = (
        (grid.dimensions.z // 2 + 1)
        if door_point.y == 0.5
        else door_point.y * (grid.dimensions.z - 1)
    )

    road_point = nearest_road(origin + door_point, map)

    # Usually we should be able to find the nearest road, but otherwise we can default to the door height
    if road_point is None:
        road_point = origin + door_point

    grid.origin = ivec3(origin.x, map.height_at(road_point) - 1, origin.y)

    if stilts:
        grid.origin += ivec3(0, 3, 0)

    if not can_place_shape(shape, grid, map, urban_only, allow_water, stilts):
        return False

    # build
    place(editor, shape, grid, rng, map, style, stilts)
    return True


def can_place_shape(
    shape: BuildingShape,
    grid: Grid,
    build_map: Map,
    urban_only: bool,
    allow_water: bool = False,
    stilts: bool = False,
):
    points = set(shape.get_points_2d(grid))
    water_amt = 0
    total_height_diff = 0

    if stilts:
        points |= get_surrounding_points(points, 3)

    for point in points:
        if not build_map.is_in_bounds2d(point):
            return False

        # water check
        if build_map.water[point.x][point.y]:
            water_amt += 1

        # freeness check
        if build_map.buildings[point.x][point.y] is not None:
            return False

        # urban check
        if urban_only and (
            not build_map.districts[point.x][point.y]
            or build_map.districts[point.x][point.y].type != DistrictType.URBAN
        ):
            return False

        total_height_diff += abs(grid.origin.y - build_map.height_at(point))

    if (WATER_THRESHOLD <= water_amt / len(points)) and not allow_water:
        return False

    avg_height_diff = total_height_diff / len(points)
    return avg_height_diff < MAX_AVG_HEIGHT_DIFF


def nearest_road(start_point: ivec2, map: Map) -> ivec2 | None:
    queue = [start_point]
    visited = set()
    limit = 100
    iterations = 0

    while queue:
        point = queue.pop(0)
        visited.add(point)
        iterations += 1

        if iterations > limit:
            return None

        if map.is_in_bounds2d(point) and map.buildings[point.x][point.y] in [
            DevelopmentType.CITY_ROAD,
            DevelopmentType.CITY_WALL,
        ]:
            return point

        for direction in CARDINAL:
            neighbour = point + get_ivec2(direction)

            if map.is_in_bounds2d(neighbour) and neighbour not in visited:
                queue.append(neighbour)

    return None


PLACE_BASEMENT_CONSTANT = 2.5


def place(
    editor: Editor,
    shape: BuildingShape,
    grid: Grid,
    rng: RNG,
    build_map: Map,
    style: BuildStyle,
    stilts: bool = False,
):
    district = build_map.districts[grid.origin.x][grid.origin.z]
    palette: Palette = (
        rng.choose(district.palettes)
        if district
        else Palette.find("japanese_dark_blackstone")
    )

    plan = BuildingPlan(shape.points, grid, palette)
    plan.cell_map[ivec3(0, 0, 0)].doors.append(shape.door_direction)

    for point in shape.get_points_2d(grid):
        build_map.buildings[point.x][point.y] = DevelopmentType.BUILDING

    # Basement and foundation
    if stilts:
        build_stilt_frame(editor, rng, palette, plan, build_map)
    else:
        for cell in plan.cells:
            if cell.position.y != 0:
                continue

            height_sum = 0
            height_count = 0
            grid_height = grid.origin.y

            for point in plan.grid.get_points_at_2d(
                ivec2(cell.position.x, cell.position.y)
            ):
                world_height = build_map.height_at(point)

                height_sum += grid_height - world_height
                height_count += 1

            avg_height = height_sum / height_count

            if avg_height > PLACE_BASEMENT_CONSTANT:
                plan.add_cell(cell.position - ivec3(0, 1, 0))
                grid_height = grid.origin.y - grid.height

            for point in plan.grid.get_points_at_2d(
                ivec2(cell.position.x, cell.position.y)
            ):
                world_height = build_map.height_at(point)

                for y_coord in range(world_height, grid_height):
                    stone = palette.find_block_id(
                        BlockForm.BLOCK,
                        MaterialParameters(
                            position=ivec3(point.x, y_coord, point.y),
                            age=0,
                            shade=0.5,
                            moisture=0,
                            dithering_pattern=None,
                        ),
                        MaterialRole.PRIMARY_STONE,
                    )

                    editor.placeBlock(
                        ivec3(point.x, y_coord, point.y),
                        Block(fix_block_name(stone)),
                    )

    # Clear the area
    for point in shape.get_points(grid):
        editor.placeBlock(point, Block("air"))

    build_roof(
        plan,
        editor,
        [
            component
            for component in RoofComponent.all()
            if style.name.lower() in component.tags
        ],
        rng.next(),
    )

    clear_interiors(plan, editor)
    build_floor(plan, editor)

    walls = list(
        filter(lambda wall: style.name.lower() in wall.tags, Wall.all().copy())
    )

    build_walls(plan, editor, walls, rng)

    door_coords = None

    for cell in plan.cells:
        for direction in legacy_directions.CARDINAL:
            if cell.has_door(direction):
                door_coords = grid.get_door_coords(direction) + grid.grid_to_world(cell.position)
                break

        if door_coords:
            break

    if door_coords is None:
        return

    furnish_building(
        plan.shape,
        door_coords,
        palette,
        editor,
        grid,
        rng
    )