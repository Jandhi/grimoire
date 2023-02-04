# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\data\\tests')

# Actual file
from data.load_jsons import load_jsons, load_objects
from structures.nbt.nbt_asset import NBTAsset
from data.load_nbts import load_nbts
from building_generation.walls import wall

class Test(NBTAsset):
    pass

load_nbts('data/tests')

assert(len(Test.all()) == 1)