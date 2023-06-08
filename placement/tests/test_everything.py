# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\placement\\tests')

# Actual file
from gdpc import Editor, Block
from gdpc.vector_tools import ivec2, ivec3
from districts.generate_districts import generate_districts
from maps.water_map import get_water_map
from paths.route_highway import route_highway, fill_out_highway
from paths.build_highway import build_highway
from districts.tests.draw_districts import draw_districts
from placement.city_blocks import add_city_blocks
from utils.geometry import get_outer_points
from maps.map import Map
from data.load_assets import load_assets
from terrain.smooth_edges import smooth_edges
from terrain.plateau import plateau
from palette.palette import Palette
from noise.rng import RNG
from districts.wall import build_wall_palisade, order_wall_points, build_wall_standard, build_wall_standard_with_inner, get_wall_points
from maps.building_map import BUILDING
from terrain.logger import log_trees
from maps.build_map import get_build_map
from districts.district_painter import replace_ground, plant_forest, replace_ground_smooth
from districts.paint_palette import PaintPalette
from terrain.forest import Forest
from sets.find_outer_points import find_outer_and_inner_points


SEED = 0xbab
DO_TERRAFORMING = False

editor = Editor(buffering=True, caching=True)
load_assets('assets')

area = editor.getBuildArea()
editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

log_trees(editor, build_rect, world_slice)

editor.flushBuffer() # this is needed to reload the world slice properly
print("Reloading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice reloaded!")

map = Map(world_slice)
districts, district_map = generate_districts(SEED, build_rect, world_slice, map.water)
map.districts = district_map

# set up palettes
eligible_palettes = list(filter(lambda palette : 'japanese' in palette.tags, Palette.all()))
rng = RNG(SEED, 'palettes')

for district in districts:
    palettes = [Palette.find('dwarven'), Palette.find('dwarven'), Palette.find('dwarven')]

    for i in range(3):    
        district.palettes.append(rng.pop(palettes))

# plateau stuff
if DO_TERRAFORMING:
    print('starting plateauing')
    for district in districts:
        if not district.is_urban:
            continue

        plateau(district, district_map, world_slice, editor, map.water)

    editor.flushBuffer() # this is needed to reload the world slice properly
    print('Reloading worldSlice')
    world_slice = editor.loadWorldSlice(build_rect)
    map.world = world_slice

    smooth_edges(build_rect, districts, district_map, world_slice, editor, map.water)

    editor.flushBuffer() # this is needed to reload the world slice properly
    print('Reloading worldSlice')
    world_slice = editor.loadWorldSlice(build_rect)
    map.world = world_slice
    map.correct_district_heights(districts)
# done

inner_points = []

for x in range(build_rect.size.x):
    for z in range(build_rect.size.y):
        district = district_map[x][z]

        if district is None:
            continue
        elif district.is_urban:
            inner_points.append(ivec2(x,z))

wall_points, wall_dict = get_wall_points(inner_points, world_slice)
wall_points = order_wall_points(wall_points, wall_dict)

rng = RNG(SEED)
palette = Palette.find('dwarven')

build_map = get_build_map(world_slice)

urban_road : PaintPalette = PaintPalette.find('urban_road')
#replace_ground_smooth(inner_points, urban_road.palette, rng, map.water, build_map, editor, world_slice)

# draw_districts(districts, build_rect, district_map, map.water, world_slice, editor)

# for district in districts:
#     x = district.origin.x
#     z = district.origin.z

#     y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z] + 10 
#     editor.placeBlock((x, y, z), Block('sea_lantern'))

add_city_blocks(editor, districts, map, SEED, is_debug=False)

# WALL

#uncomment one of these to test one of the three wall types

#build_wall_standard_with_inner(wall_points, wall_dict, inner_points, editor, map.world, map.water, rng, palette)
#build_wall_palisade(wall_points, editor, map.world, map.water, rng, palette)
#build_wall_standard(wall_points, wall_dict, inner_points, editor, map.world, map.water, palette)

ignore_blocks = [
    'minecraft:sand',
    'minecraft:gravel',
    'minecraft:stone',
    'minecraft:copper_ore'
]


# test : PaintPalette = PaintPalette.find('farmland')
# test2 : PaintPalette = PaintPalette.find('wheat')
# forest : Forest = Forest.find('mixed_forest')
# rural_road : PaintPalette = PaintPalette.find('rural_road')

# options = [forest]
# for district in districts:

#     if district.is_urban == False: 
#         choice = rng.choose(options)
#         outer_district_points, inner_district_points = find_outer_and_inner_points(district.points_2d, 4)
#         if choice == forest:
#             plant_forest(list(inner_district_points), forest, rng, map.water, build_map, editor, world_slice, ignore_blocks)
#         elif choice == test:
#             replace_ground(list(inner_district_points), test.palette, rng, map.water, build_map, editor, world_slice, 0, ignore_blocks)
#             replace_ground(list(inner_district_points), test2.palette, rng, map.water, build_map, editor, world_slice, 1, ignore_blocks)
#             replace_ground(list(outer_district_points), rural_road.palette, rng, map.water, build_map, editor, world_slice)
#         else:
#             continue
        