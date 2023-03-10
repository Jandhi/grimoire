from structures.nbt.nbt_asset import NBTAsset
from gdpc.editor import Editor
from structures.nbt.build_nbt import build_nbt
from structures.transformation import Transformation
from structures.grid import Grid
from structures.directions import right, left, opposites
from utils.tuples import add_tuples
from buildings.walls.wall import Wall
from data.asset import default_subtype

# Blueprint type for Wall
class WallBlueprint(Wall):
    pass
       