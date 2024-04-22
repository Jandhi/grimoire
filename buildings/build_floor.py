from gdpc import Block, Editor
from buildings.building_plan import BuildingPlan
from structures.grid import Grid
from gdpc.vector_tools import ivec3


def build_floor(plan: BuildingPlan, editor: Editor, build_ceiling=True):
    grid: Grid = plan.grid

    for cell in plan.cells:
        block = Block(f"{plan.palette.secondary_wood}_planks")
        pos = grid.grid_to_world(cell.position)

        for x in range(grid.width):
            for z in range(grid.depth):
                editor.placeBlock(pos + ivec3(x, 0, z), block)

                if build_ceiling:
                    editor.placeBlock(pos + ivec3(x, grid.height - 1, z), block)
