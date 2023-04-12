from structures.nbt.nbt_asset import NBTAsset
from gdpc.editor import Editor
from structures.transformation import Transformation
from structures.grid import Grid
from structures.directions import right, left, opposites
from buildings.walls.wall import Wall
from data.asset import default_subtype

# NBT class for walls
@default_subtype(Wall)
class WallNBT(NBTAsset, Wall):
    type_name = 'wall_nbt'
    facing : str
       