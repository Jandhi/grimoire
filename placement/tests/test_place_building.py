# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\placement\\tests')

# Actual file
from gdpc import Editor, Block
from gdpc.vector_tools import ivec2, ivec3
from districts.generate_districts import generate_districts
from maps.water_map import get_water_map
from districts.tests.draw_districts import draw_districts
from placement.city_blocks import add_city_blocks
from maps.map import Map
from data.load_assets import load_assets
from terrain.smooth_edges import smooth_edges
from terrain.plateau import plateau
from placement.building_placement import place_building
from structures.directions import x_plus, x_minus, z_plus, z_minus
from noise.rng import RNG

SEED = 0x030377
DO_TERRAFORMING = False

editor = Editor(buffering=True, caching=True)
load_assets('assets')

area = editor.getBuildArea()
editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

map = Map(world_slice)
rng = RNG(SEED)

editor.placeBlock(ivec3(50, -50, 50), Block('glowstone'))
place_building(editor, ivec2(50, 50), map, z_plus, rng, False)