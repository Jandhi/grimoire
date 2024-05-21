# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix("tests\\districts")

# Actual file
from grimoire.core.maps import get_water_map, Map
from tests.districts.draw_districts import draw_districts
from grimoire.districts.generate_districts import generate_districts
from gdpc import Editor, Block
from gdpc.vector_tools import ivec2, ivec3
from grimoire.terrain.tree_cutter import log_trees
from grimoire.terrain.smooth_edges import smooth_edges
from grimoire.terrain.plateau import plateau
from grimoire.districts.district_analyze import district_analyze, district_classification, super_district_classification
from tests.districts.place_colors import get_color_differentiated

SEED = 754

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
districts, district_map, super_districts, super_district_map = generate_districts(SEED, build_rect, world_slice, map)
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

SUPER_DISTRICT = True

if SUPER_DISTRICT:

    for district in super_districts:
        district_analyze(district, map)
        block = get_color_differentiated(district, super_districts, False)

        print(f"BLock: {block}  ID: {district.id}   Area: {len(district.points)}  WATER: {district.water_percentage}   FOREST: {district.forested_percentage}    ROUGHNESS: {district.roughness}    GRADIENT: {district.gradient}") #    BIOMES: {district.biome_dict}  BLOCKS: {district.surface_blocks}")

    district_classification(districts)
    super_district_classification(super_districts)

    draw_districts(super_districts, build_rect, super_district_map, map, super_district_map, editor)

else:
    for district in districts:
        district_analyze(district, map)
        block = get_color_differentiated(district, districts, False)

        print(f"BLock: {block}  ID: {district.id}   Area: {len(district.points)}  WATER: {district.water_percentage}   FOREST: {district.forested_percentage}    ROUGHNESS: {district.roughness}    GRADIENT: {district.gradient}") #    BIOMES: {district.biome_dict}  BLOCKS: {district.surface_blocks}")


    district_classification(districts)

    draw_districts(district, build_rect, district_map, map, super_district_map, editor)
