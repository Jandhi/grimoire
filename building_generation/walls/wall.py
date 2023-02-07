from data.asset import Asset
from data.asset import Asset
from gdpc.interface import Interface
from structures.grid import Grid

# Abstract class for walls
class Wall(Asset):
    def build(
        self, 
        interface: Interface, 
        grid: Grid, 
        grid_coordinate: tuple[int, int, int], 
        facing: str = None):
            pass
       