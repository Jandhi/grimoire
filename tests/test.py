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

build_map = Map(world_slice)

print(
editor.getBlock(build_map.make_3d(ivec2(0, 0)) - ivec3(0, 1, 0))
)
