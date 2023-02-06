from building_generation.roofs.roof import Roof
from data.asset import default_subtype
from structures.nbt.nbt_asset import NBTAsset
from gdpc.interface import Interface
from structures.grid import Grid
from structures.nbt.build_nbt import build_nbt
from structures.transformation import Transformation

@default_subtype(Roof)
class RoofNBT(Roof, NBTAsset):
    def build(
        self, 
        interface: Interface, 
        grid: Grid, 
        grid_coordinate: tuple[int, int, int], 
        facing: str = None):
            grid.build(interface, self, grid_coordinate, facing)