# Allows code to be run in root directory
import sys

from glm import ivec2

from grimoire.buildings.building_plan import BuildingPlan
from grimoire.buildings.roofs.build_roof import build_roof
from grimoire.buildings.roofs.roof_component import RoofComponent
from grimoire.buildings.stilts import build_stilt_frame
from grimoire.core.logger import LoggerSettings, LoggingLevel
from grimoire.core.maps import Map
from grimoire.core.structures.nbt.build_nbt import build_nbt
from grimoire.core.structures.nbt.nbt_asset import NBTAsset
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


my_schem = NBTAsset()
my_schem.do_not_place = []
my_schem.submodules = []
my_schem.palette = None
my_schem.filepath = 'grimoire/asset_data/schems/medieval_walls.schem'
my_schem.origin = ivec3(0, 0, 0)

build_nbt(
    editor,
    my_schem,
    palette=None
)