# Allows code to be run in root directory
import sys

from grimoire.core.styling.palette import Palette

sys.path[0] = sys.path[0].removesuffix("tests\\buildings")

SEED = 35425

# Actual file
from gdpc.editor import Editor
from grimoire.core.structures.grid import Grid
from grimoire.buildings.walls.wall import Wall

# from buildings.roofs.roof import Roof
from grimoire.buildings.rooms.room import Room


from grimoire.core.assets.asset_loader import load_assets
from grimoire.core.structures.legacy_directions import cardinal

from grimoire.core.styling.legacy_palette import LegacyPalette
from grimoire.buildings.roofs.roof import Roof

editor = Editor(buffering=True, caching=True)

from grimoire.core.noise.rng import RNG

from gdpc.vector_tools import ivec3

area = editor.getBuildArea()
editor.transform = (area.begin.x, 3, area.begin.z)
grid = Grid(
    origin=ivec3(
        x=area.size.x // 2,
        y=-61,
        z=area.size.z // 2,
    )
)
load_assets("grimoire\\asset_data")

rng = RNG(SEED, "get_origins")

# PALETTE
palette: Palette = None  # Palette.find("japanese_dark_blackstone")

# WALLS
lower_walls: list[Wall] = [
    wall
    for wall in Wall.all()
    if "wet" in wall.tags and "lower" in wall.positions and not wall.has_door
]
upper_walls: list[Wall] = [
    wall
    for wall in Wall.all()
    if "wet" in wall.tags and "upper" in wall.positions and not wall.has_door
]

for direction in cardinal:
    # FIXME: `lower_wall` and `upper_wall` are Wall instead of NBTAsset

    grid.build(editor, rng.choose(lower_walls), palette, ivec3(0, 0, 0), direction)
    grid.build(editor, rng.choose(upper_walls), palette, ivec3(0, 1, 0), direction)

# ROOF
# roof: Roof = Roof.find(style["roof"])
# roof.build(editor, palette, grid, (0, 2, 0))

# ROOM
room: Room = Room.find("kitchen_no_window_small")
grid.build(editor, room, palette, ivec3(0, 0, 0))
