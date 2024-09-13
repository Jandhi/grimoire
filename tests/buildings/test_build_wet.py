# Allows code to be run in root directory
import sys

from glm import ivec2

from grimoire.buildings.building_plan import BuildingPlan
from grimoire.buildings.roofs.build_roof import build_roof
from grimoire.buildings.roofs.roof_component import RoofComponent
from grimoire.buildings.stilts import build_stilt_frame
from grimoire.core.logger import LoggerSettings, LoggingLevel
from grimoire.core.maps import Map
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

from grimoire.core.styling.legacy_palette import LegacyPalette
from grimoire.buildings.roofs.roof import Roof

editor = Editor(buffering=True, caching=True)

from grimoire.core.noise.rng import RNG

from gdpc.vector_tools import ivec3, CARDINALS

area = editor.getBuildArea()
editor.transform = (area.begin.x, 3, area.begin.z)
world_slice = editor.loadWorldSlice()

load_assets(
    "grimoire\\asset_data", LoggerSettings(minimum_console_level=LoggingLevel.WARNING)
)

build_map = Map(world_slice)

rng = RNG(SEED, "get_origins")

grid = Grid(
    origin=ivec3(
        x=area.size.x // 2,
        y=build_map.height_at(ivec2(area.size.x // 2, area.size.z // 2)),
        z=area.size.z // 2,
    )
)

# PALETTE
palette: Palette = Palette.find("japanese_dark_blackstone")

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

shape = [
    ivec3(0, 0, 0),
    ivec3(0, 1, 0),
    ivec3(1, 0, 0),
    ivec3(-1, 0, 0),
    ivec3(0, 0, 1),
    ivec3(0, 0, -1),
    ivec3(0, 0, 3),
    ivec3(0, 2, 0),
    ivec3(2, 0, 0),
    ivec3(-2, 0, 0),
    ivec3(0, 0, 2),
    ivec3(0, 0, -2),
]

roof_components = [
    roof_component
    for roof_component in RoofComponent.all()
    if "japanese" in roof_component.tags
]
plan = BuildingPlan(shape, grid, palette)
build_roof(plan, editor, roof_components, SEED, build_map)

for point in shape:
    for direction in CARDINALS:
        if point + direction in shape:
            continue

        # FIXME: `lower_wall` and `upper_wall` are Wall instead of NBTAsset

        grid.build(
            editor,
            rng.choose(lower_walls if point.y == 0 else upper_walls),
            palette,
            point,
            direction,
        )

build_stilt_frame(editor, rng, palette, plan, build_map)


# ROOF
# roof: Roof = Roof.find(style["roof"])
# roof.build(editor, palette, grid, (0, 2, 0))

# ROOM
room: Room = Room.get("kitchen_no_window_small")
grid.build(editor, room, palette, ivec3(0, 0, 0))
