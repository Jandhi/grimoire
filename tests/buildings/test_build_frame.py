# Allows code to be run in root directory
import sys

from grimoire.core.maps import Map

sys.path[0] = sys.path[0].removesuffix("tests\\buildings")


from grimoire.buildings.roofs.build_roof import build_roof
from grimoire.buildings.roofs.roof_component import RoofComponent
from grimoire.core.noise.rng import RNG
from grimoire.core.styling.palette import Palette
from tests.buildings.random_shape import random_shape

# Actual file
from gdpc import Editor
from gdpc.vector_tools import ivec3
from grimoire.core.structures.grid import Grid
from grimoire.core.assets.asset_loader import load_assets
from grimoire.buildings.building_plan import BuildingPlan
from grimoire.buildings.walls.build_walls import build_walls
from grimoire.buildings.walls.wall import Wall
import grimoire.core.structures.legacy_directions as legacy_directions
from grimoire.core.styling.legacy_palette import LegacyPalette
from grimoire.buildings.build_floor import build_floor
from grimoire.buildings.rooms.furnish import furnish_building
from gdpc.vector_tools import ivec3

SEED = 0x624AAB

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

shape = random_shape(SEED)

palette = Palette.get("medieval")
plan = BuildingPlan(shape, grid, palette)
plan.palette = palette
grid.plan = plan

build_floor(plan, editor)

build_walls(
    plan,
    editor,
    [wall for wall in Wall.all() if "normal_medieval" in wall.tags],
    RNG(SEED, "build_walls"),
    build_map,
)

build_roof(
    plan,
    editor,
    [roof for roof in RoofComponent.all() if "normal_medieval" in roof.tags],
    SEED,
    build_map,
)

far_cell = max(shape, key=lambda vec: vec.x + vec.z * 10)
grid.plan.cell_map[far_cell].doors.append(legacy_directions.Z_PLUS)
door_coords = grid.get_door_coords(ivec3(0, 0, 1)) + grid.grid_to_world(far_cell)


# furnish_building(
#     plan.shape, door_coords, palette, editor, grid, rng=RNG(SEED, "furnish")
# )
