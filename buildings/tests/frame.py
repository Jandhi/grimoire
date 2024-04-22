from gdpc import Editor, Block, WorldSlice
from gdpc.vector_tools import ivec3
from structures.grid import Grid
from data.load_assets import load_assets
from utils.vectors import x_ivec3, y_ivec3, z_ivec3
from buildings.building_plan import BuildingPlan
from buildings.cell import Cell


def place_frame(cell: Cell, grid: Grid, editor: Editor):
    coords = grid.grid_to_world(cell.position)

    for x in range(grid.dimensions.x):
        editor.placeBlock(coords + x_ivec3(x), Block("red_wool"))
        editor.placeBlock(
            coords + y_ivec3(grid.height - 1) + x_ivec3(x), Block("red_wool")
        )
        editor.placeBlock(
            coords + z_ivec3(grid.depth - 1) + x_ivec3(x), Block("red_wool")
        )
        editor.placeBlock(
            coords + z_ivec3(grid.depth - 1) + y_ivec3(grid.height - 1) + x_ivec3(x),
            Block("red_wool"),
        )

    for y in range(grid.dimensions.y):
        editor.placeBlock(coords + y_ivec3(y), Block("red_wool"))
        editor.placeBlock(
            coords + x_ivec3(grid.width - 1) + y_ivec3(y), Block("red_wool")
        )
        editor.placeBlock(
            coords + z_ivec3(grid.depth - 1) + y_ivec3(y), Block("red_wool")
        )
        editor.placeBlock(
            coords + z_ivec3(grid.depth - 1) + x_ivec3(grid.width - 1) + y_ivec3(y),
            Block("red_wool"),
        )

    for z in range(grid.dimensions.z):
        editor.placeBlock(coords + z_ivec3(z), Block("red_wool"))
        editor.placeBlock(
            coords + x_ivec3(grid.width - 1) + z_ivec3(z), Block("red_wool")
        )
        editor.placeBlock(
            coords + y_ivec3(grid.height - 1) + z_ivec3(z), Block("red_wool")
        )
        editor.placeBlock(
            coords + y_ivec3(grid.height - 1) + x_ivec3(grid.width - 1) + z_ivec3(z),
            Block("red_wool"),
        )
