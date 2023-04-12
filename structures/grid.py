from structures.transformation import Transformation
from structures.nbt.build_nbt import build_nbt
from structures.directions import left, right, opposites, x_minus
from structures.nbt.build_nbt import build_nbt
from structures.transformation import Transformation
from gdpc.editor import Editor
from gdpc.nbt_tools import nbt
from structures.nbt.nbt_asset import NBTAsset
from palette.palette import Palette
from gdpc.vector_tools import ivec3

# Class to work with grids for buildings
# Local coordinates are block coordinates relative to origin of house
# World coordinates are coordinates relative to world or editor origin
# Grid coordinates are cell coordinates, with dimensinos according to the dimensions given
class Grid:
    def __init__(self, 
            dimensions : ivec3 = (7, 5, 7), 
            origin     : ivec3 = (0, 0, 0),
            ) -> None:
        self.width, self.height, self.depth = dimensions
        self.origin = origin

    def dimensions(self) -> ivec3:
        return ivec3(self.width, self.height, self.depth)

    # Coordinates functions
    def grid_to_local(self, coordinates : ivec3) -> ivec3:
        return ivec3(
            x = coordinates.x * (self.dimensions().x - 1),
            y = coordinates.y * (self.dimensions().y - 1),
            z = coordinates.z * (self.dimensions().z - 1),
        )

    def grid_to_world(self, coordinates : ivec3) -> ivec3:
        return self.local_to_world(self.grid_to_local(coordinates))

    def local_to_world(self, coordinates : ivec3) -> ivec3:
        return coordinates + self.origin

    # If on the boundary of two tiles, it will prefer the right one
    def local_to_grid(self, coordinates : ivec3) -> ivec3:
        return ivec3(
            x = coordinates.x // (self.dimensions().x - 1),
            y = coordinates.y // (self.dimensions().y - 1),
            z = coordinates.z // (self.dimensions().z - 1),
        )
    
    def world_to_local(self, coordinates : ivec3) -> ivec3:
        return coordinates - self.origin

    def world_to_grid(self, coordinates : ivec3) -> ivec3:
        return self.local_to_grid(self.world_to_local(coordinates))

    # helper function to build things on grid
    def build(self, editor : Editor, asset : NBTAsset, palette: Palette, grid_coordinate : ivec3, facing : str = None):
        local_coords = self.grid_to_local(grid_coordinate)

        if facing is None or not hasattr(asset, 'facing') or asset.facing == facing:
            return build_nbt(editor, asset, palette, Transformation(
                offset = local_coords + ivec3(0, 0, 0),
            ))
        
        if right[asset.facing] == facing:
            return build_nbt(editor, asset, palette, Transformation(
                offset=local_coords + ivec3(0, 0, 0),
                diagonal_mirror=True
            ))

        if left[asset.facing] == facing:
            return build_nbt(editor, asset, palette, Transformation(
                offset=local_coords + ivec3(0, 0, self.depth - 1),
                diagonal_mirror=True,
                mirror=(True, False, False),
            ))

        if opposites[asset.facing] == facing:
            return build_nbt(editor, asset, palette, Transformation(
                offset=local_coords + ivec3(self.width - 1, 0, 0),
                mirror=(True, False, False)
            ))