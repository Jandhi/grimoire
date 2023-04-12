from dataclasses import dataclass
from structures.grid import Grid
from buildings.cell import Cell
from gdpc.vector_tools import ivec3

@dataclass
class BuildingPlan:
    grid : Grid
    shape : list[ivec3]
    cells : dict[ivec3, Cell]

    def __init__(self, shape : list[ivec3]) -> None:
        self.shape = shape
        self.cells = {pt : Cell(position=pt, plan=self) for pt in shape}