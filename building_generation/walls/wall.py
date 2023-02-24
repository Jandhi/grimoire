from data.asset import Asset
from data.asset import Asset
from gdpc.editor import Editor
from structures.grid import Grid

# Abstract class for walls
class Wall(Asset):
    def build(
        self, 
        editor: Editor, 
        grid: Grid, 
        grid_coordinate: tuple[int, int, int], 
        facing: str = None):
            pass
       