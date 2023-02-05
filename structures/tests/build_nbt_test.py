# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\structures\\tests')

# Actual file
from gdpc.interface import requestPlayerArea, Interface
from structures.nbt.build_nbt import build_nbt
from structures.nbt.nbt_asset import NBTAsset
from structures.transformation import Transformation

area = requestPlayerArea()

print(area)

x_mid = (area[3] + area[0]) // 2 + 1 # player x
z_mid = (area[5] + area[2]) // 2 + 1 # player z

interface = Interface(x_mid, 4, z_mid, buffering=True, caching=True)

nbt_asset = NBTAsset.new(
    name     = 'test',
    type     = 'wall',
    filepath = 'assets/walls/medieval/medieval_stone_wall_door.nbt',
    origin   = (0, 0, 0)
)

build_nbt(
    interface = interface, 
    asset = nbt_asset,
    transformation=Transformation(
        mirror=(True, False, False),
        #diagonal_mirror=True,
    ),
)

interface.sendBlocks()