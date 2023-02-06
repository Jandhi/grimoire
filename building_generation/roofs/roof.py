from data.asset import Asset, asset_defaults
from gdpc.interface import Interface
from structures.grid import Grid
from structures.directions import x_minus

# Abstract base class for roofs, including roof nbts and roof blueprints
@asset_defaults(facing=x_minus)
class Roof(Asset):
    shape : list[tuple[int, int, int]]
    facing : str

    def on_construct(self):
        super().on_construct()
        self.shape = [tuple(item) for item in self.shape]

    # Abstract
    def build(self,
        interface : Interface, 
        grid : Grid,
        grid_coordinate : tuple[int, int, int],
        facing : str = None):
        pass