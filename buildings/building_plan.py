from dataclasses import dataclass
from structures.grid import Grid
from buildings.cell import Cell
from gdpc.vector_tools import ivec3
from palette.palette import Palette


@dataclass
class BuildingPlan:
    grid: Grid
    shape: list[ivec3]
    cells: list[Cell]
    cell_map: dict[ivec3, Cell]
    palette: Palette

    def __init__(self, shape: list[ivec3], grid: Grid, palette: Palette) -> None:
        self.shape = shape
        self.cell_map = {pt: Cell(position=pt, plan=self) for pt in shape}
        self.cells = list(self.cell_map.values())
        self.grid = grid
        self.palette = palette
