# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\building_generation\\tests')

# Actual file
from gdpc.interface import Interface
from structures.grid import Grid
from building_generation.walls.wall import Wall
from building_generation.roofs.roof_nbt import Roof
from data.load_assets import load_assets
from structures.directions import cardinal

interface = Interface(0, 3, 0, buffering=True, caching=True)
grid = Grid()
load_assets('assets')

# WALLS
lower_wall : Wall = Wall.find('japanese_wall_bottom_plain')
upper_wall : Wall = Wall.find('japanese_wall_upper_traps')

for direction in cardinal:
    grid.build(interface, lower_wall, (0, 0, 0), direction)
    grid.build(interface, upper_wall, (0, 1, 0), direction)

# ROOF
roof : Roof = Roof.find('japanese_roof_flat_brick_single')
grid.build(interface, roof, (0, 2, 0))

interface.sendBlocks()