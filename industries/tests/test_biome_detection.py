import sys
sys.path[0] = sys.path[0].removesuffix('\\industries\\tests')

from gdpc import Editor
from gdpc.vector_tools import ivec2, ivec3
from gdpc.world_slice import getBiome
from districts.tests.place_colors import get_color_differentiated, place_relative_to_ground

def detect_biome(districts, build_rect, district_map, water_map, world_slice, editor):
    editor = Editor(buffering=True, caching=True)

    area = editor.getBuildArea()
    editor.transform = (area.begin.x, 0, area.begin.z)

    print("Loading world slice...")
    build_rect = area.toRect()
    world_slice = editor.loadWorldSlice(build_rect)
    print("World slice loaded!")    # I imagine this is unnecessary, but leaving it in for now

    y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z]
    player_pos = ivec3(area.size.x // 2, y, area.size.z // 2)

    print(getBiome(player_pos)) 
    # Placeholder until the gruntwork of 'biome -> primary industry -> secondary industry' web is written