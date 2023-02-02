from gdpc.interface import Interface
from building_generation.wall import Wall
from structures.build_nbt import build_nbt
from structures.transformation import Transformation
from structures.grid import Grid
from structures.directions import right, left, opposites
from utils.tuples import add_tuples

def build_wall_on_grid(
        interface : Interface, 
        grid : Grid,
        grid_coordinate : tuple[int, int, int],
        wall : Wall,
        facing : str
    ):
    local_coords = grid.grid_to_local(grid_coordinate)

    if wall.facing == facing:
        build_nbt(interface, wall, Transformation(
            offset=add_tuples((0, 1, 0), local_coords),
        ))
    
    if right[wall.facing] == facing:
        build_nbt(interface, wall, Transformation(
            offset=add_tuples((0, 1, 0), local_coords),
            diagonal_mirror=True
        ))

    if left[wall.facing] == facing:
        build_nbt(interface, wall, Transformation(
            offset=add_tuples((0, 1, grid.depth - 1), local_coords),
            diagonal_mirror=True,
            mirror=(True, False, False),
        ))

    if opposites[wall.facing] == facing:
        build_nbt(interface, wall, Transformation(
            offset=add_tuples((grid.width - 1, 1, 0), local_coords),
            mirror=(True, False, False)
        ))
