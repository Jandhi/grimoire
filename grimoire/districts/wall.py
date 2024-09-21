from gdpc import Block, Editor, WorldSlice
from gdpc.vector_tools import ivec2, ivec3, dropY

from grimoire.core.styling.legacy_palette import LegacyPalette, fix_block_name
from grimoire.core.styling.materials.gradient import (
    Gradient,
    GradientAxis,
    PerlinSettings,
)
from ..core.maps import Map

from ..core.noise.random import randrange
from ..core.noise.rng import RNG
from ..core.structures.legacy_directions import (
    CARDINAL,
    NORTH,
    get_ivec2,
    ivec2_to_dir,
    opposite,
    RIGHT,
    to_text,
    vector,
)
from ..core.styling.blockform import BlockForm
from ..core.styling.materials import placer
from ..core.styling.materials.material import MaterialFeature, Material
from ..core.styling.materials.painter import PalettePainter
from ..core.styling.materials.placer import Placer
from ..core.styling.materials.traversal import MaterialTraversalStrategy
from ..core.styling.palette import Palette, MaterialRole
from ..core.utils.geometry import (
    get_neighbours_in_set,
    is_straight_ivec2,
    is_point_surrounded_dict,
    get_outer_points,
)
from ..core.utils.misc import is_water
from ..core.structures.nbt.build_nbt import build_nbt_legacy, build_nbt
from ..core.structures.nbt.nbt_asset import NBTAsset
from ..core.structures.transformation import Transformation
from ..core.styling.blockform import BlockForm
from ..core.utils.geometry import (
    get_neighbours_in_set,
    get_outer_points,
    is_point_surrounded_dict,
    is_straight_ivec2,
)
from ..core.utils.misc import is_water
from ..core.utils.remap import remap_threshold_high
from ..districts.gate import Gate, add_gates


def get_wall_points(inner_points, world_slice):
    wall_points, wall_dict = get_outer_points(inner_points, world_slice)
    for point in wall_points:
        neighbours = get_neighbours_in_set(point, inner_points)
        if len(neighbours) == 1 and wall_dict.get(neighbours[0]) == True:
            wall_points.remove(point)
            wall_dict.pop(point)
    return wall_points, wall_dict


def find_wall_neighbour(current: ivec2, wall_dict: dict, ordered_wall_dict: dict):
    for check in [
        ivec2(-1, 0),
        ivec2(0, -1),
        ivec2(-1, -1),
        ivec2(-1, 1),
        ivec2(1, -1),
        ivec2(1, 0),
        ivec2(0, 1),
        ivec2(1, 1),
    ]:  # prefers to go right
        if current is None:  # error case
            return None
        next_wall_point = current + check
        if (
            ordered_wall_dict.get(next_wall_point) != True
            and wall_dict.get(next_wall_point) == True
        ):
            return next_wall_point


# orders the list of wall points based off the first point in the list
# TODO we should probably put helpers below other functions
def order_wall_points(wall_points: list[ivec2], wall_dict: dict) -> list[list[ivec2]]:
    list_of_ordered_wall_points: list[list[ivec2]] = []
    reverse_checked = False

    if len(wall_points) < 1:
        return []

    ordered_wall_points: list[ivec2] = [wall_points.pop(0)]
    ordered_wall_dict: dict = {ordered_wall_points[0]: True}
    current_wall_point = ordered_wall_points[0]
    while wall_points:
        next_wall_point = find_wall_neighbour(
            current_wall_point, wall_dict, ordered_wall_dict
        )
        if next_wall_point is None:  # error case, clean stopping
            if (
                reverse_checked == False
            ):  # after the first error, we reverse list and check the other way
                print("reverse")
                reverse_checked = True
                ordered_wall_points.reverse()
                current_wall_point = ordered_wall_points[-1]
            else:
                print("failed")
                reverse_checked = False
                if (  # NOTE, look at this later
                    len(ordered_wall_points) > 20
                ):  # prevent weird small wall segements, story again to see if its improvement or not
                    list_of_ordered_wall_points.append(ordered_wall_points)
                ordered_wall_points = []
                ordered_wall_points.append(wall_points.pop(0))
                ordered_wall_dict[ordered_wall_points[0]] = True
                current_wall_point = ordered_wall_points[0]
        else:
            # print(next_wall_point)
            wall_points.remove(next_wall_point)
            ordered_wall_points.append(next_wall_point)
            ordered_wall_dict[next_wall_point] = True
            current_wall_point = next_wall_point

    list_of_ordered_wall_points.append(ordered_wall_points)
    return list_of_ordered_wall_points


# currently not in use, adapt this function to point to the appropriate further build wall likely in the future
def build_wall(
    wall_points: list[ivec2],
    wall_dict: dict,
    editor: Editor,
    world_slice: WorldSlice,
    rng: RNG,
    wall_type: str,
    palette: Palette,
) -> list[Gate]:
    if wall_type == "palisade":
        return build_wall_palisade(wall_points, editor, world_slice, rng, palette)
    elif wall_type == "standard":
        return build_wall_standard(
            wall_points, wall_dict, editor, world_slice, rng, palette
        )


def build_wall_palisade(
    wall_points: list[ivec2],
    editor: Editor,
    world_slice: WorldSlice,
    water_map: dict,
    rng: RNG,
    palette: Palette,
    build_map: Map,
) -> list[Gate]:

    # TODO cleanup the wall_points here to match the format mostly in the other build wall functions, then readress the build gate and can make it cleaner
    new_wall_points = []
    height_map = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    # enhancing the wall_points list by adding height
    height = randrange(rng.value(), 4, 7)
    for vec in wall_points:
        point = [vec.x, height_map[vec.x][vec.y], vec.y]
        point += [height]
        new_wall_points.append(point)
        # ensuring next wall piece is a different height
        next_height = randrange(rng.value(), 4, 7)
        while height == next_height:
            next_height = randrange(rng.value(), 4, 7)
        height = next_height

    # sorting by height, so lowest sections get built first
    unordered_wall_points = (
        new_wall_points  # keep a copy of the list not sorted by height
    )
    # new_wall_points.sort(key = lambda a: a[3])

    for point in new_wall_points:
        if water_map[point[0]][point[2]] == False:
            for y in range(point[1], point[1] + point[3]):
                # interface.placeBlock(point[0],y,point[2], 'minecraft:stone_bricks')
                # interface.placeBlock(point[0],point[1] + point[3], point[2], 'minecraft:stone_brick_wall')

                wood = palette.find_block_id(
                    BlockForm.BLOCK,
                    MaterialRole.PILLAR,
                )

                editor.placeBlock((point[0], y, point[2]), Block(wood))

            wood = palette.find_block_id(
                BlockForm.FENCE,
                MaterialRole.SECONDARY_WOOD,
            )

            editor.placeBlock(
                (point[0], point[1] + point[3], point[2]),
                Block(wood),
            )

    return add_gates(
        unordered_wall_points, editor, world_slice, True, None, palette, build_map, True
    )


def build_wall_standard(
    wall_points: list[ivec2],
    wall_dict: dict,
    inner_points: list[ivec2],
    editor: Editor,
    world_slice: WorldSlice,
    build_map: Map,
    palette: Palette,
) -> list[Gate]:
    wall_points = add_wall_points_height(wall_points, world_slice)
    wall_points = add_wall_points_directionality(wall_points, wall_dict, inner_points)
    wall_points = check_water(wall_points, build_map)
    height_map = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

    previous_dir = NORTH

    walkway_list = (
        []
    )  # idea is to get this list and then get the new inner points of hte wall, how do I get height to those
    walkway_dict: dict = {}

    rng = RNG(0)

    for i, wall_point in enumerate(wall_points):
        point = wall_point[0]

        painter = create_wall_painter(
            editor, palette, build_map, height_map[point.x, point.z], point.y
        )

        if wall_point[2] == "water":
            continue
        else:
            if wall_point[2] == "water_wall":
                fill_water(ivec2(point.x, point.z), editor, height_map, world_slice)

            for y in range(height_map[point.x, point.z], point.y + 1):
                painter.place_block(
                    ivec3(point.x, y, point.z),
                    MaterialRole.PRIMARY_STONE,
                    BlockForm.BLOCK,
                )

                # editor.placeBlock((point.x, y, point.z), Block(full_block))
            if len(wall_point[1]) != 0:
                previous_dir = wall_point[1][0]

            painter.place_block(
                ivec3(point.x, point.y + 1, point.z),
                MaterialRole.PRIMARY_STONE,
                BlockForm.STAIRS,
                states={"facing": to_text(RIGHT[previous_dir])},
            )

            for dir in wall_point[1]:
                height_modifier = 0  # used in one case to alter height of walkway
                if i not in [0, len(wall_points) - 1]:
                    prev_h = wall_points[i - 1][0].y
                    next_h = wall_points[i + 1][0].y
                    h = point.y
                    if prev_h == h - 1 and next_h == h - 1:
                        height_modifier = -1
                if RIGHT[dir] in wall_point[1]:  # add corner bits for walkway
                    for new_pt in (
                        point + vector(dir) + vector(RIGHT[dir]),
                        point + vector(dir) + vector(RIGHT[dir]) * 2,
                        point + vector(dir) * 2 + vector(RIGHT[dir]),
                    ):
                        if wall_dict.get(ivec2(new_pt.x, new_pt.z)) == True:
                            break
                        if walkway_dict.get(ivec2(new_pt.x, new_pt.z)) is None:
                            walkway_list.append(ivec2(new_pt.x, new_pt.z))
                            walkway_dict[ivec2(new_pt.x, new_pt.z)] = (
                                new_pt.y + height_modifier
                            )
                for x in range(1, 4):
                    new_pt = point + vector(dir) * x
                    if wall_dict.get(ivec2(new_pt.x, new_pt.z)) == True:
                        break
                    if walkway_dict.get(ivec2(new_pt.x, new_pt.z)) is None:
                        walkway_list.append(ivec2(new_pt.x, new_pt.z))
                        walkway_dict[ivec2(new_pt.x, new_pt.z)] = (
                            new_pt.y + height_modifier
                        )

    flatten_walkway(walkway_list, walkway_dict, editor, palette=palette)
    return add_gates(wall_points, editor, world_slice, True, None, palette, build_map)


def build_wall_standard_with_inner(
    wall_points: list[ivec2],
    wall_dict: dict,
    inner_points: list[ivec2],
    editor: Editor,
    world_slice: WorldSlice,
    build_map: Map,
    rng: RNG,
    palette: Palette,
) -> list[Gate]:
    wall_points = add_wall_points_height(wall_points, world_slice)
    wall_points = add_wall_points_directionality(wall_points, wall_dict, inner_points)
    wall_points = check_water(wall_points, build_map)
    height_map = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

    previous_dir = NORTH

    walkway_list = (
        []
    )  # idea is to get this list and then get the new inner points of hte wall, how do I get height to those
    walkway_dict: dict = {}

    inner_wall_list = []
    inner_wall_dict: dict = {}

    for i, wall_point in enumerate(wall_points):
        point = wall_point[0]
        fill_in = False
        if wall_point[2] == "water":
            continue
        else:

            painter = create_wall_painter(
                editor, palette, build_map, height_map[point.x, point.z], point.y
            )

            # check if need to fill in this wall slice
            if (
                i == 0
                or i == len(wall_points) - 1
                or wall_points[i + 1][2] == "water"
                or wall_points[i - 1][2] == "water"
                or point.y > wall_points[i - 1][0].y + 4
                or point.y > wall_points[i + 1][0].y + 4
            ):
                fill_in = True

            elif wall_point[2] == "water_wall":  # not in current use, perhaps future
                fill_water(ivec2(point.x, point.z), editor, height_map, world_slice)

            for y in range(height_map[point.x, point.z], point.y + 1):
                painter.place_block(
                    ivec3(point.x, y, point.z),
                    MaterialRole.PRIMARY_STONE,
                    BlockForm.BLOCK,
                )
            if len(wall_point[1]) != 0:
                previous_dir = wall_point[1][0]

            painter.place_block(
                ivec3(point.x, point.y + 1, point.z),
                MaterialRole.PRIMARY_STONE,
                BlockForm.STAIRS,
                states={"facing": to_text(RIGHT[previous_dir])},
            )

            for dir in wall_point[1]:
                height_modifier = 0  # used in one case to alter height of walkway
                if i not in [0, len(wall_points) - 1]:
                    prev_h = wall_points[i - 1][0].y
                    next_h = wall_points[i + 1][0].y
                    h = point.y
                    if prev_h == h - 1 and next_h == h - 1:
                        height_modifier = -1
                if RIGHT[dir] in wall_point[1]:  # add corner bits for walkway
                    for new_pt in (
                        point + vector(dir) + vector(RIGHT[dir]),
                        point + vector(dir) + vector(RIGHT[dir]) * 2,
                        point + vector(dir) * 2 + vector(RIGHT[dir]),
                    ):
                        if wall_dict.get(ivec2(new_pt.x, new_pt.z)) == True:
                            break
                        if walkway_dict.get(ivec2(new_pt.x, new_pt.z)) is None:
                            walkway_list.append(ivec2(new_pt.x, new_pt.z))
                            walkway_dict[ivec2(new_pt.x, new_pt.z)] = (
                                new_pt.y + height_modifier
                            )
                        if fill_in:
                            for y in range(height_map[new_pt.x, new_pt.z], point.y):
                                painter.place_block(
                                    ivec3(new_pt.x, y, new_pt.z),
                                    MaterialRole.PRIMARY_STONE,
                                    BlockForm.BLOCK,
                                )
                            if build_map.water_at(new_pt.xz):
                                fill_water(
                                    ivec2(new_pt.x, new_pt.z),
                                    editor,
                                    height_map,
                                    world_slice,
                                )

                    # inner wall
                    for wall_pt in (
                        point + vector(dir) * 2 + vector(RIGHT[dir]) * 2,
                        point + vector(dir) + vector(RIGHT[dir]) * 3,
                        point + vector(dir) * 3 + vector(RIGHT[dir]),
                    ):
                        if (
                            wall_dict.get(ivec2(wall_pt.x, wall_pt.z)) != True
                            and walkway_dict.get(ivec2(wall_pt.x, wall_pt.z)) is None
                        ):
                            inner_wall_list.append(ivec3(wall_pt.x, point.y, wall_pt.z))
                for x in range(1, 4):
                    new_pt = point + vector(dir) * x
                    if wall_dict.get(ivec2(new_pt.x, new_pt.z)) == True:
                        break
                    if walkway_dict.get(ivec2(new_pt.x, new_pt.z)) is None:
                        walkway_list.append(ivec2(new_pt.x, new_pt.z))
                        walkway_dict[ivec2(new_pt.x, new_pt.z)] = (
                            new_pt.y + height_modifier
                        )
                        # inner wall
                        if x == 3:
                            wall_pt = point + vector(dir) * 4
                            if (
                                wall_dict.get(ivec2(wall_pt.x, wall_pt.z)) != True
                                and walkway_dict.get(ivec2(wall_pt.x, wall_pt.z))
                                is None
                            ):
                                inner_wall_list.append(
                                    ivec3(wall_pt.x, point.y, wall_pt.z)
                                )
                    if fill_in:
                        for y in range(height_map[new_pt.x, new_pt.z], point.y):
                            painter.place_block(
                                ivec3(new_pt.x, y, new_pt.z),
                                MaterialRole.PRIMARY_STONE,
                                BlockForm.BLOCK,
                            )
                        if build_map.water_at(new_pt.xz):
                            fill_water(
                                ivec2(new_pt.x, new_pt.z),
                                editor,
                                height_map,
                                world_slice,
                            )

    for pt in inner_wall_list:
        painter = create_wall_painter(
            editor, palette, build_map, height_map[pt.x, pt.z], pt.y
        )

        if (
            walkway_dict.get(ivec2(pt.x, pt.z)) is None
        ):  # check again since walkway was not completed as inner wall was being added
            inner_wall_dict[ivec2(pt.x, pt.z)] = (
                True  # can put something else here if needed
            )
            for y in range(height_map[pt.x, pt.z], pt.y + 1):
                painter.place_block(
                    ivec3(pt.x, y, pt.z), MaterialRole.PRIMARY_STONE, BlockForm.BLOCK
                )
            if build_map.water_at(
                pt.xz
            ):  # behaviour is to place inner wall into water til floor
                fill_water(ivec2(pt.x, pt.z), editor, height_map, world_slice)

    walkway_dict = flatten_walkway(walkway_list, walkway_dict, editor, palette=palette)
    add_towers(walkway_list, walkway_dict, editor, rng, palette, build_map)
    return add_gates(
        wall_points,
        editor,
        world_slice,
        False,
        inner_wall_dict,
        palette=palette,
        build_map=build_map,
    )


# adds direction to the wall points to know which way we need to build walkways
def add_wall_points_directionality(
    wall_points: list[ivec3], wall_dict: dict, inner_points: list[ivec2]
):
    enhanced_wall_points = []
    for point in wall_points:
        enhanced_point = [point, [], None]
        ivec2_point = ivec2(point.x, point.z)
        neighbours = get_neighbours_in_set(ivec2_point, inner_points)
        for neighbour in neighbours:
            if not wall_dict.get(neighbour):
                enhanced_point[1].append(ivec2_to_dir(neighbour - ivec2_point))

        enhanced_wall_points.append(enhanced_point)

    return enhanced_wall_points


WALL_HEIGHT = 10  # max height of wall


def add_wall_points_height(wall_points: list[ivec2], world_slice: WorldSlice):
    height_wall_points = []
    height_map = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    current_height = height_map[wall_points[0].x, wall_points[0].y]
    target_height = current_height
    for i, point in enumerate(wall_points):
        if i % 5 == 0:
            if len(wall_points) - 1 < i + 5:
                target_height = height_map[
                    wall_points[0].x, wall_points[0].y
                ]  # wrap around a bit
            else:
                target_height = height_map[wall_points[i + 5].x, wall_points[i + 5].y]
            if target_height > current_height + (
                WALL_HEIGHT * 2 / 3
            ) or target_height < current_height + (
                WALL_HEIGHT * 2 / 3
            ):  # deal with small height anomalies by looking for a point a bit further
                if len(wall_points) - 1 < i + 10:
                    target_height = height_map[
                        wall_points[0].x, wall_points[0].y
                    ]  # wrap around a bit
                else:
                    target_height = height_map[
                        wall_points[i + 10].x, wall_points[i + 10].y
                    ]
        # add a check to see for drastic height difference
        if (
            current_height
            < height_map[wall_points[i].x, wall_points[i].y] - WALL_HEIGHT * 2 / 3
        ):
            current_height = height_map[wall_points[i].x, wall_points[i].y]
            target_height = current_height
        elif current_height != target_height and (1 < i < len(wall_points) - 2):
            if is_straight_ivec2(wall_points[i - 2], wall_points[i + 2], 4):
                if current_height < target_height:
                    current_height += 1
                elif current_height > target_height:
                    current_height -= 1
        new_point = ivec3(point.x, current_height + WALL_HEIGHT, point.y)
        height_wall_points.append(new_point)

    return height_wall_points


RANGE = 3  # range for walkway flattening
NEIGHBOURS = [
    (x, z) for x in range(-RANGE, RANGE + 1) for z in range(-RANGE, RANGE + 1)
]


def flatten_walkway(
    walkway_list: list[ivec2],
    walkway_dict: dict,
    editor: Editor,
    palette: Palette,
):
    for point in walkway_list:
        walkway_dict[point] = average_neighbour_height(point.x, point.y, walkway_dict)

    painter = PalettePainter(editor, palette)

    # first pass places slabs and changes dict heights
    for key, height in walkway_dict.items():
        if (
            height % 1 <= 0.25
            or not 0.25 < height % 1 <= 0.5
            and not 0.5 < height % 1 <= 0.75
        ):
            painter.place_block(
                ivec3(key.x, round(height), key.y),
                MaterialRole.SECONDARY_WOOD,
                BlockForm.SLAB,
            )

            walkway_dict[key] = round(height)
        elif 0.25 < height % 1 <= 0.5:
            painter.place_block(
                ivec3(key.x, round(height), key.y),
                MaterialRole.SECONDARY_WOOD,
                BlockForm.SLAB,
                states={"type": "top"},
            )
            walkway_dict[key] = round(height) + 0.49
        else:
            painter.place_block(
                ivec3(key.x, round(height) - 1, key.y),
                MaterialRole.SECONDARY_WOOD,
                BlockForm.SLAB,
                states={"type": "top"},
            )
            walkway_dict[key] = round(height) - 0.51
    # 2nd pass to add stairs based on first pass changes
    for key in walkway_dict:
        height = walkway_dict[key]
        for direction in CARDINAL:
            delta = get_ivec2(direction)
            neighbour = key + delta
            if walkway_dict.get(neighbour) is None:
                continue
            elif height % 1 == 0:  # bottom slab
                if walkway_dict.get(neighbour) - height >= 1:
                    painter.place_block(
                        ivec3(key.x, round(height), key.y),
                        MaterialRole.SECONDARY_WOOD,
                        BlockForm.STAIRS,
                        states={"facing": to_text(direction)},
                    )
            elif walkway_dict.get(neighbour) - height <= -1:
                painter.place_block(
                    ivec3(key.x, round(height), key.y),
                    MaterialRole.SECONDARY_WOOD,
                    BlockForm.STAIRS,
                    states={"facing": to_text(opposite(direction))},
                )

    return walkway_dict


def average_neighbour_height(x: int, z: int, walkway_dict: dict) -> int:
    height_sum = 0
    total_weight = 0

    for dx, dz in NEIGHBOURS:
        if (
            ivec2(x + dx, z + dz) not in walkway_dict
        ):  # we only need to flatten for within a districts
            continue
        elif (
            abs(walkway_dict[ivec2(x + dx, z + dz)] - walkway_dict[ivec2(x, z)]) >= 4
        ):  # ignore extremes
            continue

        distance = abs(dx) + abs(dz)
        weight = 0.8**distance
        height = walkway_dict[ivec2(x + dx, z + dz)]
        height_sum += height * weight
        total_weight += weight

    return height_sum // total_weight


WATER_CHECK = 5  # the water the distance the wall will build across


# water checking
def check_water(wall_points: list[ivec3], build_map: Map):
    buildable = False  # bool, if true, set to water_wall, water otherwise
    long_water = (
        True  # assume water start NOTE: changed hardcoding so wall can spawn in water
    )
    for i, wall_pt in enumerate(wall_points):
        point: ivec3 = wall_pt[0]

        if build_map.water_at(dropY(point)):
            wall_points[i][2] = "water_wall"

            # more complex attempt at having wall be able to bridge some water, implement better later
            # NOTE: Commented out for now, readdress later
            # if long_water:
            #     wall_points[i][2] = "water"
            # elif buildable:
            #     wall_points[i][2] = "water_wall"
            #
            # else:  # check if can bridge
            #     wall_points[i][2] = "water"  # default
            #     for a in range(1, WATER_CHECK + 1):
            #         if a + i >= len(wall_points):  # OUT OF BOUNDS
            #             break
            #         pt = wall_points[a + i][0]
            #         if not build_map.water_at(point.xz):  # found land within range
            #             buildable = True
            #             long_water = False
            #             wall_points[i][2] = "water_wall"
            #             break
            #         elif a == WATER_CHECK:
            #             long_water = True
        else:
            buildable = False  # reset buildability
            long_water = False

    return wall_points


def fill_water(pt: ivec2, editor: Editor, height_map: dict, world_slice: WorldSlice):
    height = height_map[pt.x, pt.y] - 1
    while is_water(ivec3(pt.x, height, pt.y), world_slice) and height != 0:
        editor.placeBlock((pt.x, height, pt.y), Block("minecraft:mossy_stone_bricks"))
        height = height - 1


def create_wall_painter(
    editor: Editor, palette: Palette, build_map: Map, lowest_y: int, highest_y: int
) -> PalettePainter:
    moisture_func = remap_threshold_high(
        Gradient(13, build_map, 0.6, PerlinSettings(20, 8, 2))
        .with_axis(GradientAxis.y(lowest_y, highest_y, True))
        .to_func(),
        0.3,
    )

    wear_func = remap_threshold_high(
        Gradient(17, build_map, 0.8, PerlinSettings(40, 8, 2))
        .with_axis(GradientAxis.y(lowest_y, highest_y, True))
        .to_func(),
        0.3,
    )

    return (
        PalettePainter(editor, palette)
        .with_feature(
            MaterialFeature.SHADE,
            Gradient(10, build_map, noise_settings=PerlinSettings(20, 8, 2))
            .with_axis(GradientAxis.y(lowest_y, highest_y))
            .to_func(),
        )
        .with_feature(
            MaterialFeature.MOISTURE,
            moisture_func,
        )
        .with_feature(MaterialFeature.WEAR, wear_func)
    )


def add_towers(
    walkway_list: list[ivec2],
    walkway_dict: dict,
    editor: Editor,
    rng: RNG,
    palette: Palette,
    build_map: Map,
):
    distance_to_next_tower = 80  # minimum
    tower_possible = randrange(
        rng.value(), 0, distance_to_next_tower // 2
    )  # counter if 0, allow a tower to be built
    tower = NBTAsset.construct(
        name="tower",
        type="tower",
        filepath="grimoire/asset_data/city_wall/towers/basic_tower.nbt",
        origin=(3, 1, 3),
        palette=Palette.get("wall_palette"),
    )

    for point in walkway_list:
        if tower_possible == 0:
            # print("tower possible")
            if is_point_surrounded_dict(point, walkway_dict):
                tower_possible = distance_to_next_tower

                point_height = round(walkway_dict.get(point))

                painter = create_wall_painter(
                    editor, palette, build_map, build_map.height_at(point), point_height
                )

                # prep tower base
                neighbours = [
                    ivec2(x, z)
                    for x in range(point.x - 2, point.x + 3)
                    for z in range(point.y - 2, point.y + 3)
                ]

                for neighbour in neighbours:
                    for height in range(point_height - 1, point_height + 6):
                        if (
                            height == point_height + 5
                            or walkway_dict.get(neighbour) is None
                        ):
                            painter.place_block(
                                ivec3(neighbour.x, height, neighbour.y),
                                MaterialRole.PRIMARY_STONE,
                                BlockForm.BLOCK,
                            )

                # build tower
                painter.place_nbt(
                    asset=tower,
                    transformation=Transformation(
                        offset=ivec3(point.x, point_height + 6, point.y),
                        mirror=(True, False, False),
                        # diagonal_mirror=True,
                    ),
                )
                # else:
                #    print("actually it isnt")
        else:
            tower_possible -= 1
