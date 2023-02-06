from building_generation.roofs.roof_base import RoofBase
from structures.nbt.nbt_asset import NBTAsset
from gdpc.interface import Interface
from structures.grid import Grid
from structures.nbt.build_nbt import build_nbt
from structures.transformation import Transformation

class Roof(RoofBase, NBTAsset):
    def build(
        self, 
        interface: Interface, 
        grid: Grid, 
        grid_coordinate: tuple[int, int, int], 
        facing: str):
            build_nbt(
                interface,
                self,
                Transformation(
                    
                ),
            )