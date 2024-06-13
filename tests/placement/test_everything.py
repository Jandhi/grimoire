# Allows code to be run in root directory
import sys
import time

from gdpc.vector_tools import addY, dropY, rotate3D

from grimoire.core.structures import legacy_directions
from grimoire.core.structures.legacy_directions import VECTORS
from grimoire.core.styling.palette import BuildStyle, Palette
from grimoire.paths.build_highway import build_highway
from grimoire.paths.route_highway import fill_out_highway, route_highway
from grimoire.paths.signposts import build_signpost

sys.path[0] = sys.path[0].removesuffix("/tests/placement")
print(f"PATH: {sys.path[0]}")

# Actual file
from gdpc import Block, Box, Editor
from gdpc.lookup import GRANULARS
from glm import ivec2

from grimoire.core.assets.asset_loader import load_assets
from grimoire.core.maps import DevelopmentType, Map, get_build_map
from grimoire.core.noise.rng import RNG
from grimoire.core.utils.sets.find_outer_points import find_outer_and_inner_points
from grimoire.districts.district import District, DistrictType, SuperDistrict
from grimoire.districts.district_analyze import (
    district_analyze,
    district_classification,
    super_district_classification,
)
from grimoire.districts.district_painter import (
    plant_forest,
    replace_ground,
    replace_ground_smooth,
)
from grimoire.districts.generate_districts import generate_districts
from grimoire.districts.paint_palette import PaintPalette
from grimoire.districts.wall import (
    build_wall_standard_with_inner,
    get_wall_points,
    order_wall_points,
)
from grimoire.industries.biomes import desert, forest, rocky, snowy
from grimoire.industries.industry import get_district_biomes
from grimoire.placement.city_blocks import add_city_blocks
from grimoire.terrain.forest import Forest
from grimoire.terrain.plateau import plateau
from grimoire.terrain.smooth_edges import smooth_edges
from grimoire.terrain.tree_cutter import log_trees

SEED = 0x4473
DO_TERRAFORMING = False  # Set this to true for the final iteration
LOG_TREES = True
DO_WALL = False
DO_RURAL = False

SLEEP_DELAY = 1

editor = Editor(buffering=True, caching=True)
load_assets("grimoire/asset_data")

area = editor.getBuildArea()

# can't to do areas too large yet
if area.size.x > 1000:
    x = area.center.x - 400
    z = area.center.z - 400
    editor.setBuildArea(Box((x, 0, z), (350, area.size.y, 350)))

area = editor.getBuildArea()

editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

if LOG_TREES:  # TO DO, only log urban
    log_trees(editor, build_rect, world_slice)

editor.flushBuffer()  # this is needed to reload the world slice properly
print("Reloading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice reloaded!")

main_map = Map(world_slice)
districts, district_map, super_districts, super_district_map = generate_districts(
    SEED, build_rect, world_slice, main_map
)
main_map.districts = district_map
main_map.super_districts = super_district_map

# plateau stuff
if DO_TERRAFORMING:  # think about terraforming deal with districts/superdistricts
    print("starting plateauing")
    for district in districts:
        if not district.is_urban:
            continue

        plateau(district, district_map, world_slice, editor, main_map.water)

    editor.flushBuffer()  # this is needed to reload the world slice properly
    print("Reloading worldSlice")
    world_slice = editor.loadWorldSlice(build_rect)
    main_map.world = world_slice

    smooth_edges(
        build_rect, districts, district_map, world_slice, editor, main_map.water
    )

    editor.flushBuffer()  # this is needed to reload the world slice properly
    print("Reloading worldSlice")
    world_slice = editor.loadWorldSlice(build_rect)
    main_map.world = world_slice
    main_map.correct_district_heights(districts)
# done

print("sleepy time to reduce http traffic")
time.sleep(SLEEP_DELAY)  # to try to reduce http traffic, we'll do a little sleepy time

for district in super_districts:
    district_analyze(district, main_map)

district_classification(districts)
super_district_classification(super_districts)

inner_points = []

biomes = {}
for district in super_districts:
    for biome in district.biome_dict:
        if biome not in biomes:
            biomes[biome] = 0

        biomes[biome] += district.biome_dict[biome]

most_prevalent_biome = max(biomes.items(), key=lambda kp: kp[1])[0]

style = BuildStyle.DESERT

# FIXME: Incomplete code!
if most_prevalent_biome in []:
    style = BuildStyle.WET

for x in range(build_rect.size.x):
    for z in range(build_rect.size.y):
        super_district = super_district_map[x][z]

        if super_district is None:
            continue
        elif super_district.type == DistrictType.URBAN:
            inner_points.append(ivec2(x, z))


# set up palettes
eligible_palettes = list(
    filter(lambda palette: style.name.lower() in palette.tags, Palette.all())
)
rng = RNG(SEED, "palettes")

for district in districts:
    palettes = eligible_palettes.copy()

    for _ in range(min(3, len(eligible_palettes))):
        district.palettes.append(rng.pop(palettes))

wall_points, wall_dict = get_wall_points(inner_points, world_slice)
wall_points_list = order_wall_points(wall_points, wall_dict)

rng = RNG(SEED)
palette = rng.choose(eligible_palettes)

build_map = get_build_map(world_slice, 20)

# FIXME: Not guaranteed to find the "urban_road" PaintPalette!
urban_road: PaintPalette = (
    PaintPalette.find("desert_road")
    if style == BuildStyle.DESERT
    else PaintPalette.find("urban_road")
)


# draw_districts(districts, build_rect, district_map, map.water, world_slice, editor)

# for districts in districts:
#     x = districts.origin.x
#     z = districts.origin.z

#     y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z] + 10
#     editor.placeBlock((x, y, z), Block('sea_lantern'))

(blocks, inners, outers) = add_city_blocks(
    editor, super_districts, main_map, SEED, style=style, is_debug=False, stilts=False
)

city_roads = set()

for outer in outers:
    city_roads |= outer

# WALL

# uncomment one of these to story one of the three wall types

if DO_WALL:
    wall_points, wall_dict = get_wall_points(inner_points, world_slice)
    wall_points_list = order_wall_points(wall_points, wall_dict)

    for wall_points in wall_points_list:
        gates = build_wall_standard_with_inner(
            wall_points,
            wall_dict,
            inner_points,
            editor,
            world_slice,
            main_map.water,
            rng,
            palette,
        )

        for gate in gates:
            path_origin = gate.location + rotate3D(VECTORS[gate.direction] * -3, 1)

            size = main_map.world.rect.size

            path_end: ivec2 = None
            if gate.direction == legacy_directions.SOUTH:
                path_end = ivec2(gate.location.x, 0)
            if gate.direction == legacy_directions.NORTH:
                path_end = ivec2(gate.location.x, size.y - 1)
            if gate.direction == legacy_directions.WEST:
                path_end = ivec2(size.x - 1, gate.location.z)
            if gate.direction == legacy_directions.EAST:
                path_end = ivec2(0, gate.location.z)

            def round_to_four(vec: ivec2) -> ivec2:
                return ivec2(vec.x - vec.x % 4, vec.y - vec.y % 4)

            point_a = addY(round_to_four(dropY(path_origin)), gate.location.y)
            point_b = main_map.make_3d(round_to_four(path_end))

            highway = route_highway(point_a, point_b, main_map, editor, is_debug=True)
            if highway:
                highway = fill_out_highway(highway)
                build_highway(highway, editor, world_slice, main_map)
                build_signpost(editor, highway, main_map, rng)


replace_ground_smooth(
    list(city_roads),
    urban_road.palette,
    rng,
    main_map.water,
    build_map,
    editor,
    world_slice,
)

# build_wall_palisade(wall_points, editor, map.world, map.water, rng, palette)
# build_wall_standard(wall_points, wall_dict, inner_points, editor, map.world, map.water, palette)

if DO_RURAL:
    ignore_blocks = GRANULARS | {
        "minecraft:stone",
        "minecraft:copper_ore",
    }

    farmland: PaintPalette = PaintPalette.find("farmland")
    forests = Forest.all()
    crops = list(filter(lambda palette: "crops" in palette.tags, PaintPalette.all()))
    rural_road: PaintPalette = PaintPalette.find("rural_road")

    options = forests + crops

    for super_district in super_districts:
        if super_district == DistrictType.RURAL:
            # FIXME: Undefined words "mountainous" etc.
            if mountainous and not is_snowy or is_desert:
                choice_list = rng.choose([[None], [None], [None], [None]])
            elif is_snowy and not mountainous:
                choice_list = rng.choose([forests, [None], [None], [None]])
            else:
                choice_list = rng.choose([crops, forests, [None], [None]])
            choice = rng.choose(choice_list)

            outer_district_points, inner_district_points = find_outer_and_inner_points(
                super_district.points_2d, 4
            )
            if isinstance(choice, Forest):  # forest
                plant_forest(
                    list(inner_district_points),
                    choice,
                    rng,
                    main_map.water,
                    build_map,
                    editor,
                    world_slice,
                    ignore_blocks,
                )
            elif isinstance(choice, PaintPalette):  # crops
                replace_ground(
                    list(inner_district_points),
                    farmland.palette,
                    rng,
                    main_map.water,
                    build_map,
                    editor,
                    world_slice,
                    0,
                    ignore_blocks,
                )
                replace_ground(
                    list(inner_district_points),
                    choice.palette,
                    rng,
                    main_map.water,
                    build_map,
                    editor,
                    world_slice,
                    1,
                    ignore_blocks,
                )
                replace_ground(
                    list(outer_district_points),
                    rural_road.palette,
                    rng,
                    main_map.water,
                    build_map,
                    editor,
                    world_slice,
                )
            else:
                continue

            time.sleep(
                5
            )  # to try to reduce http traffic, we'll do a little sleepy time
