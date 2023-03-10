# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\building_generation\\tests')

# Actual file
from gdpc.editor import Editor
from structures.grid import Grid
from buildings.walls.wall import Wall
from buildings.roofs.roof import Roof
from buildings.rooms.room import Room

from data.load_assets import load_assets
from structures.directions import cardinal

from style.style import Style
from palette.palette import Palette

editor = Editor(transformLike=(0, -61, 0), buffering=True, caching=True)
grid = Grid()
load_assets('assets')

