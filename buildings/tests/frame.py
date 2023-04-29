from gdpc import Editor, Block, WorldSlice
from gdpc.vector_tools import ivec3
from structures.grid import Grid
from data.load_assets import load_assets
from utils.vectors import x_vec, y_vec, z_vec
from buildings.building_plan import BuildingPlan
from buildings.cell import Cell


def place_frame(cell : Cell, grid : Grid, editor : Editor):
    coords = grid.grid_to_world(cell.position)

    for x in range(grid.dimensions.x):
        editor.placeBlock(coords + x_vec(x), Block('red_wool'))
        editor.placeBlock(coords + y_vec(grid.height - 1) + x_vec(x), Block('red_wool'))
        editor.placeBlock(coords + z_vec(grid.depth - 1) + x_vec(x), Block('red_wool'))
        editor.placeBlock(coords + z_vec(grid.depth - 1) + y_vec(grid.height - 1) + x_vec(x), Block('red_wool'))

    for y in range(grid.dimensions.y):
        editor.placeBlock(coords + y_vec(y), Block('red_wool'))
        editor.placeBlock(coords + x_vec(grid.width - 1) + y_vec(y), Block('red_wool'))
        editor.placeBlock(coords + z_vec(grid.depth - 1) + y_vec(y), Block('red_wool'))
        editor.placeBlock(coords + z_vec(grid.depth - 1) + x_vec(grid.width - 1) +y_vec(y), Block('red_wool'))

    for z in range(grid.dimensions.z):
        editor.placeBlock(coords + z_vec(z), Block('red_wool'))
        editor.placeBlock(coords + x_vec(grid.width - 1) + z_vec(z), Block('red_wool'))
        editor.placeBlock(coords + y_vec(grid.height - 1) + z_vec(z), Block('red_wool'))
        editor.placeBlock(coords + y_vec(grid.height - 1) + x_vec(grid.width - 1) + z_vec(z), Block('red_wool'))