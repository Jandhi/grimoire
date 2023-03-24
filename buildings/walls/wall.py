from data.asset import Asset
from data.asset import Asset
from gdpc.editor import Editor
from structures.grid import Grid
from structures.types import vec3

# Abstract class for walls
class Wall(Asset):
    def build(
        self, 
        editor: Editor, 
        grid: Grid, 
        grid_coordinate: vec3, 
        facing: str = None):
            pass
       