# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\districts\\tests')

# Actual file
from gdpc import Editor, Block
from gdpc.vector_tools import ivec2, ivec3
from districts.generate_districts_testing import generate_districts
from maps.water_map import get_water_map
from districts.tests.draw_districts import draw_districts
from terrain.logger import log_trees
from terrain.smooth_edges import smooth_edges
from terrain.plateau import plateau
from maps.map import Map
from districts.district_analyze import district_analyze

SEED = 752

DO_TERRAFORMING = False

editor = Editor(buffering=True, caching=True)

area = editor.getBuildArea()
editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

#log_trees(editor, build_rect, world_slice)

editor.flushBuffer() # this is needed to reload the world slice properly
print("Reloading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice reloaded!")

water_map = get_water_map(world_slice)
map = Map(world_slice)
districts, district_map = generate_districts(SEED, build_rect, world_slice, map)
map.districts = district_map

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

draw_districts(districts, build_rect, district_map, water_map, world_slice, editor)

for district in districts:
    x = district.origin.x
    z = district.origin.z

    y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z] + 10
    #editor.placeBlock((x, y, z), Block('sea_lantern'))
    district_analyze(district, map)
    print(f"ID: {district.id}   Area: {len(district.points)}  WATER: {district.water_percentage}   FOREST: {district.forested_percentage}    ROUGHNESS: {district.roughness}    GRADIENT: {district.gradient}     BIOMES: {district.biome_dict}  BLOCKS: {district.surface_blocks}")