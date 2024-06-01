# Allows code to be run in root directory
import sys

from glm import ivec2

from grimoire.core.styling.palette import BuildStyle
from grimoire.districts.district import District

sys.path[0] = sys.path[0].removesuffix("tests\\placement")

# Actual file
import itertools

from gdpc import Block, Editor
from gdpc.geometry import line3D

from grimoire.core.assets.asset_loader import load_assets
from grimoire.core.maps import DevelopmentType, Map
from grimoire.core.noise.rng import RNG
from grimoire.core.structures.legacy_directions import get_ivec2
from grimoire.core.styling.legacy_palette import LegacyPalette
from grimoire.core.utils.bounds import area_2d
from grimoire.core.utils.geometry import get_outer_points
from grimoire.core.utils.vectors import y_ivec3
from grimoire.districts.generate_districts import generate_districts
from grimoire.districts.wall import build_wall_standard_with_inner, order_wall_points
from grimoire.paths.build_highway import build_highway
from grimoire.paths.route_highway import fill_out_highway, route_highway
from grimoire.placement.city_blocks import add_city_blocks
from grimoire.terrain.plateau import plateau
from grimoire.terrain.smooth_edges import smooth_edges

SEED = 77273
DO_TERRAFORMING = False

editor = Editor(buffering=True, caching=True)
load_assets("grimoire/asset_data")

area = editor.getBuildArea()


editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

world_map = Map(world_slice)
districts, district_map, _, _ = generate_districts(
    SEED, build_rect, world_slice, world_map
)
world_map.districts = district_map
# draw_districts(districts, build_rect, district_map, map.water, world_slice, editor)

# set up palettes
eligible_palettes = list(
    filter(lambda palette: BuildStyle.DESERT in palette.tags, LegacyPalette.all())
)
rng = RNG(SEED, "palettes")

for district in districts:
    palettes = eligible_palettes.copy()

    for _ in range(3):
        district.palettes.append(rng.pop(palettes))

# plateau stuff
if DO_TERRAFORMING:
    print("starting plateauing")
    for district in districts:
        if not district.is_urban:
            continue

        plateau(district, district_map, world_slice, editor, world_map.water)

    editor.flushBuffer()  # this is needed to reload the world slice properly
    print("Reloading worldSlice")
    world_slice = editor.loadWorldSlice(build_rect)
    world_map.world = world_slice

    smooth_edges(
        build_rect, districts, district_map, world_slice, editor, world_map.water
    )

    editor.flushBuffer()  # this is needed to reload the world slice properly
    print("Reloading worldSlice")
    world_slice = editor.loadWorldSlice(build_rect)
    world_map.world = world_slice
    world_map.correct_district_heights(districts)
# done

map.copy_heightmaps()


# ground
def place_at_ground(x, z, block_name) -> None:
    y = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][x][z]
    editor.placeBlock((x, y - 1, z), Block(block_name))


def replace_ground(
    points: list[ivec2], block_dict: dict[Block, int], rng: RNG, water_map
) -> None:
    for point in points:
        if (
            water_map[point.x][point.y] == False
            and world_map.buildings[point.x][point.y] != DevelopmentType.BUILDING
        ):
            block: Block = rng.choose_weighted(block_dict)
            place_at_ground(point.x, point.y, block)


test_blocks = {
    "stone": 3,
    "cobblestone": 2,
    "stone_bricks": 8,
    "andesite": 3,
    "gravel": 1,
}

test_blocks_dirt: dict[str, int] = {
    "rooted_dirt": 3,
    "dirt": 4,
    "podzol": 2,
    "coarse_dirt": 3,
}

inner_points: list[ivec2] = []

for x, z in itertools.product(range(build_rect.size.x), range(build_rect.size.y)):
    district = district_map[x][z]

    if district is None:
        continue
    elif district.is_urban:
        inner_points.append(ivec2(x, z))

wall_points, wall_dict = get_outer_points(inner_points, world_slice)
wall_points_list: list[list[ivec2]] = order_wall_points(wall_points, wall_dict)

rng = RNG(SEED)
palette = LegacyPalette.find("desert_dark_prismarine")

# can use either test_blocks for more urban or test_blocks_dirt for dirty ground
# replace_ground(inner_points, test_blocks, rng, map.water)

# WALL

# uncomment one of these to story one of the three wall types


for wall_points in wall_points_list:
    gates = build_wall_standard_with_inner(
        wall_points,
        wall_dict,
        inner_points,
        editor,
        world_map.world,
        world_map.water,
        rng,
        palette,
    )
# gates = build_wall_palisade(wall_points, editor, map.world, map.water, rng, palette)
# gates = build_wall_standard(wall_points, wall_dict, inner_points, editor, map.world, map.water, palette)

world_map._calculate_near_wall(districts)

for gate in gates:
    size = ivec2(12, 12)
    for offset in area_2d(size):
        point = (
            ivec2(gate.location.x, gate.location.z) + offset - size / 2
        )  # half size to center it

        if not world_map.is_in_bounds2d(point):
            continue

        world_map.buildings[point.x][point.y] = DevelopmentType.GATE

    vec = get_ivec2(gate.direction)
    route_start2d = ivec2(gate.location.x, gate.location.z) + 5 * vec
    district = world_map.districts[route_start2d.x][route_start2d.y]

    route_start = world_map.make_3d(route_start2d)

    if district is not None and not district.is_urban:
        d_avg = district.average()
        d_mid = world_map.make_3d(ivec2(d_avg.x, d_avg.z))

        for point in line3D(d_mid + y_ivec3(30), route_start + y_ivec3(30)):
            editor.placeBlock(point, Block("red_wool"))

        route = route_highway(route_start, d_mid, world_map, editor, is_debug=False)

        if route is None:
            continue

        route = fill_out_highway(route)
        build_highway(route, editor, world_map.world, world_map)

        # final connection
        route = route_highway(
            gate.location, route_start, world_map, editor, is_debug=False
        )
        route = fill_out_highway(route)
        build_highway(route, editor, world_map.world, world_map)


for district in districts:
    x = district.origin.x
    z = district.origin.z

    y = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][x][z] + 10
    editor.placeBlock((x, y, z), Block("sea_lantern"))

add_city_blocks(editor, districts, world_map, SEED, is_debug=True)
