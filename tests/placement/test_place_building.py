# Allows code to be run in root directory
import sys

from grimoire.core.styling.palette import BuildStyle

sys.path[0] = sys.path[0].removesuffix("tests\\placement")

# Actual file
from gdpc import Editor, Block
from gdpc.vector_tools import ivec2, ivec3
from grimoire.core.maps import Map
from grimoire.core.assets.asset_loader import load_assets
from grimoire.placement.building_placement import attempt_place_building
from grimoire.core.structures.legacy_directions import Z_PLUS
from grimoire.core.noise.rng import RNG


SEED = 92198129812
DO_TERRAFORMING = False

editor = Editor(buffering=True, caching=True)
load_assets("grimoire/asset_data")

area = editor.getBuildArea()
editor.transform = (area.begin.x, 0, area.begin.z)
print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

map = Map(world_slice)
rng = RNG(SEED)

editor.placeBlock(ivec3(50, 100, 50), Block("glowstone"))
attempt_place_building(
    editor,
    ivec2(50, 50),
    map,
    Z_PLUS,
    rng,
    urban_only=False,
    style=BuildStyle.DESERT,
)
