# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\building_generation\\tests')

# Actual file
from gdpc.interface import Interface
from structures.grid import Grid
from building_generation.walls.wall import Wall
from building_generation.roofs.roof import Roof
from building_generation.rooms.room import Room

from data.load_assets import load_assets
from structures.directions import cardinal

from style.style import Style
from palette.palette import Palette

interface = Interface(0, 3, 0, buffering=True, caching=True)
grid = Grid()
load_assets('assets')

styles = {
    'japanese' : {
        'lower' : 'japanese_wall_bottom_plain',
        'upper'  : 'japanese_wall_upper_traps',
        'roof'   : 'japanese_roof_flat_brick_single'
    },
    'viking' : {
        'lower'  : 'viking_wall_lower_stone_base_window',
        'upper'  : 'viking_wall_upper_logs_window',
        'roof'   : 'viking_roof_stone_accent_single'
    }
}
style = styles['viking']

# PALETTE
palette : Palette = Palette.find('acacia_palette')

# WALLS
lower_wall : Wall = Wall.find(style['lower'])
upper_wall : Wall = Wall.find(style['upper'])

for direction in cardinal:
    grid.build(interface, lower_wall, palette, (0, 0, 0), direction)
    grid.build(interface, upper_wall, palette, (0, 1, 0), direction)

# ROOF
roof : Roof = Roof.find(style['roof'])
roof.build(interface, palette, grid, (0, 2, 0))

# ROOM
room : Room = Room.find('kitchen_no_window_small')
grid.build(interface, room, palette, (0, 0, 0))

interface.sendBlocks()