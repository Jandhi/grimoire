# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\structures\\tests')

# Actual file
from gdpc.editor import Editor
from structures.nbt.build_nbt import build_nbt
from structures.nbt.nbt_asset import NBTAsset
from palette.palette import Palette
from structures.transformation import Transformation
from data.load_assets import load_assets
from structures.asset_structure import AssetStructure
from gdpc.vector_tools import ivec3
from terrain.water_map import get_water_map
from terrain.build_map import get_build_map
from structures.well import Well

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

load_assets('assets')
y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][0][0]

test : AssetStructure = AssetStructure.find('well')

build_nbt(
    editor = editor, 
    asset = test,
    palette = None,
    transformation=Transformation(
        offset= ivec3(area.middle.x,y,area.middle.z),
        mirror=(True, False, True),
        #diagonal_mirror=True,
    ),
)



#well
#test_well = Well(ivec3(area.middle.x,y,area.middle.z))
#test_well.build(editor)