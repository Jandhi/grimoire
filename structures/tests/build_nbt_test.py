# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\structures\\tests')

# Actual file
from gdpc.editor import Editor
from gdpc.editor_tools import centerBuildAreaOnPlayer
from structures.nbt.build_nbt import build_nbt
from structures.nbt.nbt_asset import NBTAsset
from palette.palette import Palette
from structures.transformation import Transformation


editor = Editor(transformLike=(0, -60, 0), buffering=True, caching=True)

nbt_asset = NBTAsset.construct(
    name     = 'test',
    type     = 'wall',
    filepath = 'assets/walls/medieval/medieval_stone_wall_door.nbt',
    origin   = (0, 0, 0),
    palette =  Palette.construct(name='test')
)

build_nbt(
    editor = editor, 
    asset = nbt_asset,
    palette = Palette.construct(name='test'),
    transformation=Transformation(
        mirror=(True, False, False),
        #diagonal_mirror=True,
    ),
)