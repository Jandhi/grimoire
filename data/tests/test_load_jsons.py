# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\data\\tests')

# Actual file
from data.load_jsons import load_jsons, load_objects
from structures.nbt.nbt_asset import NBTAsset
from data.load_assets import load_assets
from building_generation.walls import wall_nbt

class Test(NBTAsset):
    pass

class SubTest(Test):
    pass

load_assets('data/tests')

# you should see one error and two warnings about fields not being annotated
assert(len(Test.all()) == 2)
assert(len(SubTest.all()) == 1)