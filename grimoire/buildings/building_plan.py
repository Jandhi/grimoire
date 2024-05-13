from dataclasses import dataclass
from ..core.structures.grid import Grid
from ..buildings.legacycell import LegacyCell
from gdpc.vector_tools import ivec3
from grimoire.core.styling.legacy_palette import LegacyPalette


@dataclass
class BuildingPlan:
    grid: Grid
    shape: list[ivec3]
    cells: list[LegacyCell]
    cell_map: dict[ivec3, LegacyCell]
    palette: LegacyPalette

    def __init__(self, shape: list[ivec3], grid: Grid, palette: LegacyPalette) -> None:
        self.shape = shape
        self.cell_map = {pt: LegacyCell(position=pt, plan=self) for pt in shape}
        self.cells = list(self.cell_map.values())
        self.grid = grid
        self.palette = palette
