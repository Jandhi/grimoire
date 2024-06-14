# Allows code to be run in root directory
import sys
import time

from gdpc.vector_tools import dropY, rotate3D, addY

from grimoire.core.structures import legacy_directions
from grimoire.core.structures.legacy_directions import VECTORS
from grimoire.core.styling.palette import Palette, BuildStyle
from grimoire.paths.build_highway import build_highway
from grimoire.paths.route_highway import route_highway, fill_out_highway
from grimoire.paths.signposts import build_signpost

sys.path[0] = sys.path[0].removesuffix("\\tests\\placement")

# Actual file
from gdpc import Box, Editor
from gdpc.lookup import GRANULARS
from glm import ivec2, ivec3

from grimoire.core.assets.asset_loader import load_assets
from grimoire.core.maps import Map, get_build_map
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
DO_TERRAFORMING = True  # Set this to true for the final iteration
LOG_TRESS = True

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

if LOG_TRESS:  # TO DO, only log urban
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

forest_counter = 0
desert_counter = 0
rocky_counter = 0
snowy_counter = 0
mountainous = False
is_snowy = False
is_desert = False
for district in districts:
    biomes_in_district = get_district_biomes(editor, district)
    for biome in biomes_in_district:
        if biome in forest:
            forest_counter += 1
        elif biome in desert:
            desert_counter += 1
        elif biome in rocky:
            mountainous = True
            rocky_counter += 1
        elif biome in snowy:
            snowy_counter += 1

if rocky_counter >= len(districts) // 2:
    mountainous = True
if snowy_counter >= len(districts) // 2:
    is_snowy = True
if desert_counter >= len(districts) // 2:
    is_desert = True
biome_counters = [forest_counter, desert_counter, rocky_counter]

style = BuildStyle.JAPANESE

# if max(biome_counters) == forest_counter or max(biome_counters) not in [
#     desert_counter,
#     rocky_counter,
# ]:
#     style = BuildStyle.JAPANESE
# elif max(biome_counters) == desert_counter:
#     style = BuildStyle.DESERT
# else:
#     style = BuildStyle.DWARVEN

# set up palettes
eligible_palettes = list(
    filter(lambda palette: style.name.lower() in palette.tags, Palette.all())
)
rng = RNG(SEED, "palettes")

for district in districts:
    palettes = eligible_palettes.copy()

    for _ in range(min(3, len(eligible_palettes))):
        district.palettes.append(rng.pop(palettes))


for district in super_districts:
    district_analyze(district, main_map)

district_classification(districts)
super_district_classification(super_districts)

inner_points = []


for x in range(build_rect.size.x):
    for z in range(build_rect.size.y):
        super_district = super_district_map[x][z]

        if super_district is None:
            continue
        elif super_district.type == DistrictType.URBAN:
            inner_points.append(ivec2(x, z))

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


# WALL

# uncomment one of these to story one of the three wall types

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
        path_origin = gate.location + VECTORS[gate.direction]
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

# build_wall_palisade(wall_points, editor, map.world, map.water, rng, palette)
# build_wall_standard(wall_points, wall_dict, inner_points, editor, map.world, map.water, palette)

ignore_blocks = GRANULARS | {
    "minecraft:stone",
    "minecraft:copper_ore",
}

farmland: PaintPalette = PaintPalette.find("farmland")
forests = Forest.all()
crops = list(filter(lambda palette: "crops" in palette.tags, PaintPalette.all()))
rural_road: PaintPalette = PaintPalette.find("rural_road")

options = forests + crops
