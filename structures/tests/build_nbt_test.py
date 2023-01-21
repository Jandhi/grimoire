# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\building\\tests')

# Actual file
from gdpc.interface import requestPlayerArea, Interface
from building.build_nbt import build_nbt

area = requestPlayerArea()

print(area)

x_mid = (area[3] + area[0]) // 2 + 1 # player x
z_mid = (area[5] + area[2]) // 2 + 1 # player z

interface = Interface(x_mid, 10, z_mid, buffering=True, caching=True)

build_nbt(interface, 'assets/wall.nbt')

interface.sendBlocks()