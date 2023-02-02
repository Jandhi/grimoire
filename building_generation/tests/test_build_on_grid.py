# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\building_generation\\tests')

# Actual file
from gdpc.interface import Interface
from structures.grid import Grid
from building_generation.wall import Wall
from building_generation.build_on_grid import build_wall_on_grid
from data.load_jsons import load_objects

interface = Interface(0, 4, 0, buffering=True, caching=True)
grid = Grid()
walls = load_objects('assets/walls', Wall)
wall = walls[1]

build_wall_on_grid(interface, grid, (0, 0, 0), wall, 'x_minus')
build_wall_on_grid(interface, grid, (0, 0, 0), wall, 'x_plus')
build_wall_on_grid(interface, grid, (0, 0, 0), wall, 'z_minus')
build_wall_on_grid(interface, grid, (0, 0, 0), wall, 'z_plus')

build_wall_on_grid(interface, grid, (0, 1, 0), wall, 'z_minus')
build_wall_on_grid(interface, grid, (0, 1, 0), wall, 'z_plus')

interface.sendBlocks()