# Allows code to be run in root directory
import sys
from pathlib import Path


sys.path[0] = sys.path[0].removesuffix(str(Path("tests/placement")))
print(f"PATH: {sys.path[0]}")


from grimoire.core.maps import get_water_map, get_build_map

# Actual file
from gdpc.editor import Editor
from grimoire.core.assets.asset_loader import load_assets
from grimoire.core.structures.asset_structure import AssetStructure
from grimoire.core.structures.transformation import Transformation
from gdpc.vector_tools import ivec3
from grimoire.core.structures.nbt.build_nbt import build_nbt

SEED = 2

editor = Editor(buffering=True, caching=True)

area = editor.getBuildArea()
print(area)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")
water_map = get_water_map(world_slice)
build_map = get_build_map(world_slice, 20)

load_assets(str(Path("grimoire/asset_data")))
y = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][0][0]

well: AssetStructure = AssetStructure.get("well")

print(well)
# well
# test_well = well(ivec3(area.middle.x, y, area.middle.z))
# test_well.build(editor)
build_nbt(
    editor,
    well,
    palette=None,
    transformation=Transformation(offset=ivec3(area.middle.x, y, area.middle.z)),
)

# market
# test_market = Market(ivec3(area.middle.x, y, area.middle.z))
# test_market.place_block(editor)
