from gdpc import Block, Editor
from gdpc.vector_tools import ivec3

from ..buildings.building_plan import BuildingPlan
from ..core.structures.grid import Grid
from ..core.styling.blockform import BlockForm
from ..core.styling.palette import MaterialRole
from itertools import product


def build_floor(plan: BuildingPlan, editor: Editor, build_ceiling=True):
    """
    Builds the flooring for all cells in a BuildingPlan
    """
    grid: Grid = plan.grid

    for cell in plan.cells:

        cell_pos = grid.grid_to_world(cell.position)

    for x, z in product(range(grid.width), range(grid.depth)):
        pos = cell_pos + ivec3(x, 0, z)
        block_id = plan.palette.find_block_id(
            BlockForm.BLOCK,
            MaterialRole.SECONDARY_WOOD,
        )
        block = Block(block_id)

        editor.placeBlock(pos, block)

        if build_ceiling:
            editor.placeBlock(pos + ivec3(0, grid.height - 1, 0), block)
