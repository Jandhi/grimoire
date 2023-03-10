from dataclasses import dataclass
from structures.grid import Grid
from structures.types import vec3
from buildings.cell import Cell

@dataclass
class BuildingPlan:
    grid : Grid
    shape : list[vec3]
    cells : dict[vec3, Cell]

    def __init__(self, shape : list[vec3]) -> None:
        self.shape = shape
        self.cells = {pt : Cell(position=pt, plan=self) for pt in shape}