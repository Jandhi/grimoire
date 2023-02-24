from building_generation.roofs.roof import Roof
from data.asset import default_subtype
from structures.nbt.nbt_asset import NBTAsset
from gdpc.editor import Editor
from structures.grid import Grid
from structures.transformation import Transformation
from palette.palette import Palette

@default_subtype(Roof)
class RoofNBT(Roof, NBTAsset):
    def build(
        self, 
        editor: Editor, 
        palette :  Palette,
        grid: Grid, 
        grid_coordinate: tuple[int, int, int], 
        facing: str = None):
            grid.build(editor, self, palette, grid_coordinate, facing)