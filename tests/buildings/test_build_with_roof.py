# Allows code to be run in root directory
import sys

from grimoire.core.maps import Map

sys.path[0] = sys.path[0].removesuffix("tests\\buildings")

# Actual file
from grimoire.core.structures import legacy_directions
from grimoire.core.styling.palette import Palette, BuildStyle
from gdpc import Editor
from gdpc.vector_tools import ivec3
from grimoire.core.structures.grid import Grid
from grimoire.core.assets.asset_loader import load_assets
from grimoire.buildings.building_plan import BuildingPlan
from grimoire.buildings.walls.build_walls import build_walls
from grimoire.core.noise.rng import RNG
from grimoire.buildings.walls.wall import Wall
from grimoire.core.styling.legacy_palette import LegacyPalette
from grimoire.buildings.build_floor import build_floor
from grimoire.buildings.building_plan import BuildingPlan
from grimoire.buildings.clear_interiors import clear_interiors
from grimoire.buildings.roofs.build_roof import build_roof
from grimoire.buildings.roofs.roof_component import RoofComponent
from grimoire.buildings.rooms.furnish import furnish, furnish_building
from grimoire.buildings.walls.build_walls import build_walls
from grimoire.buildings.walls.wall import Wall
from grimoire.core.assets.asset_loader import load_assets
from grimoire.core.noise.rng import RNG
from grimoire.core.structures.grid import Grid
from grimoire.core.styling.legacy_palette import LegacyPalette

SEED = 654

editor = Editor(buffering=True, caching=True)

area = editor.getBuildArea()
editor.transform = (area.begin.x, 0, area.begin.z)
build_map = Map(editor.loadWorldSlice())

grid = Grid(
    origin=ivec3(
        x=area.size.x // 2,
        y=-61,
        z=area.size.z // 2,
    )
)
load_assets("grimoire/asset_data")

shape = [ivec3(0, 0, 0), ivec3(0, 0, 1), ivec3(1, 0, 1)]

palette = Palette.get("japanese")
plan = BuildingPlan(shape, grid, palette)

plan.cell_map[ivec3(0, 0, 0)].doors.append(legacy_directions.NORTH)

build_roof(
    plan,
    editor,
    [
        roof
        for roof in RoofComponent.all()
        if BuildStyle.NORMAL_MEDIEVAL.name.lower() in roof.tags
    ],
    SEED,
    build_map,
)

clear_interiors(plan, editor)
build_floor(plan, editor)

walls = [
    wall for wall in Wall.all() if BuildStyle.NORMAL_MEDIEVAL.name.lower() in wall.tags
]

build_walls(plan, editor, walls, RNG(SEED, "build_walls"), build_map)
