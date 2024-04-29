# Allows code to be run in root directory
import sys

sys.path[0] = sys.path[0].removesuffix("\\landmarks\\story_tests")

# Actual file
from gdpc.editor import Editor
from core.assets.load_assets import load_assets
from core.structures.asset_structure import AssetStructure
from gdpc.vector_tools import ivec3
from terrain.water_map import get_water_map
from terrain.build_map import get_build_map
from core.structures.market.market import Market

SEED = 2

editor = Editor(buffering=True, caching=True)

area = editor.getBuildArea()
print(area)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")
water_map = get_water_map(world_slice)
build_map = get_build_map(world_slice)

load_assets("assets")
y = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][0][0]

test: AssetStructure = AssetStructure.find("well")
"""
build_nbt(
    editor = editor, 
    asset = story_tests,
    palette = None,
    transformation=Transformation(
        offset= ivec3(area.middle.x,y,area.middle.z),
        mirror=(True, False, True),
        #diagonal_mirror=True,
    ),
)
"""


# well
# test_well = Well(ivec3(area.middle.x,y,area.middle.z))
# test_well.build(editor)

# market
test_market = Market(ivec3(area.middle.x, y, area.middle.z))
test_market.build(editor)
