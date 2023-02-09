from utils.tuples import sub_tuples, add_tuples, map_tuples
from structures.transformation import Transformation
from structures.nbt.build_nbt import build_nbt
from structures.directions import left, right, opposites, x_minus
from structures.nbt.build_nbt import build_nbt
from structures.transformation import Transformation
from utils.tuples import add_tuples
from gdpc.interface import Interface
from structures.nbt.nbt_asset import NBTAsset


# Class to work with grids for buildings
# Local coordinates are block coordinates relative to origin of house
# World coordinates are coordinates relative to world or interface origin
# Grid coordinates are cell coordinates, with dimensinos according to the dimensions given
class Grid:
    def __init__(self, 
            dimensions : tuple[int, int, int] = (7, 5, 7), 
            origin     : tuple[int, int, int] = (0, 0, 0),
            ) -> None:
        self.width, self.height, self.depth = dimensions
        self.origin = origin

    def dimensions(self) -> tuple[int, int, int]:
        return self.width, self.height, self.depth

    # Coordinates functions
    
    def grid_to_local(self, coordinates : tuple[int, int, int]) -> tuple[int, int, int]:
        return map_tuples(lambda coordinate, dimension : coordinate * (dimension - 1), coordinates, self.dimensions())

    def grid_to_world(self, coordinates : tuple[int, int, int]) -> tuple[int, int, int]:
        return self.local_to_world(self.grid_to_local(coordinates))

    def local_to_world(self, coordinates : tuple[int, int, int]) -> tuple[int, int, int]:
        return add_tuples(coordinates, self.origin)

    # If on the boundary of two tiles, it will prefer the right one
    def local_to_grid(self, coordinates : tuple[int, int, int]) -> tuple[int, int, int]:
        return map_tuples(lambda coordinate, dimension : coordinate // (dimension - 1), coordinates, self.dimensions())
    
    def world_to_local(self, coordinates : tuple[int, int, int]) -> tuple[int, int, int]:
        return sub_tuples(coordinates, self.origin)

    def world_to_grid(self, coordinates : tuple[int, int, int]) -> tuple[int, int, int]:
        return self.local_to_grid(self.world_to_local(coordinates))

    # helper function to build things on grid
    def build(self, interface : Interface, asset : NBTAsset, grid_coordinate : tuple[int, int, int], facing : str = None):
        local_coords = self.grid_to_local(grid_coordinate)

        if facing is None or not hasattr(asset, 'facing') or asset.facing == facing:
            return build_nbt(interface, asset, Transformation(
                offset=add_tuples((0, 0, 0), local_coords),
            ))
        
        if right[asset.facing] == facing:
            return build_nbt(interface, asset, Transformation(
                offset=add_tuples((0, 0, 0), local_coords),
                diagonal_mirror=True
            ))

        if left[asset.facing] == facing:
            return build_nbt(interface, asset, Transformation(
                offset=add_tuples((0, 0, self.depth - 1), local_coords),
                diagonal_mirror=True,
                mirror=(True, False, False),
            ))

        if opposites[asset.facing] == facing:
            return build_nbt(interface, asset, Transformation(
                offset=add_tuples((self.width - 1, 0, 0), local_coords),
                mirror=(True, False, False)
            ))