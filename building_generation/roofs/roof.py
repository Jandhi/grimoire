from data.asset import Asset, asset_defaults
from gdpc.editor import Editor
from structures.grid import Grid
from structures.directions import x_minus
from palette.palette import Palette

# Abstract base class for roofs, including roof nbts and roof blueprints
@asset_defaults(facing=x_minus)
class Roof(Asset):
    shape : list[tuple[int, int, int]]
    facing : str

    def on_construct(self):
        super().on_construct()
        self.shape = [tuple(item) for item in self.shape]

    # Abstract
    def build(
        self, 
        editor: Editor, 
        palette :  Palette,
        grid: Grid, 
        grid_coordinate: tuple[int, int, int], 
        facing: str = None):
        pass