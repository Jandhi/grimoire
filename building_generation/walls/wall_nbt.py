from structures.nbt.nbt_asset import NBTAsset
from gdpc.interface import Interface
from structures.nbt.build_nbt import build_nbt
from structures.transformation import Transformation
from structures.grid import Grid
from structures.directions import right, left, opposites
from utils.tuples import add_tuples
from building_generation.walls.wall import Wall
from data.asset import default_subtype

@default_subtype(Wall)
class WallNBT(NBTAsset, Wall):
    type_name = 'wall_nbt'
    facing : str
       