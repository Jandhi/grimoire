from . import legacy_directions
from .nbt.build_nbt import build_nbt_legacy, build_nbt
from .transformation import Transformation
from gdpc.editor import Editor
from .nbt.nbt_asset import NBTAsset
from grimoire.core.styling.legacy_palette import LegacyPalette
from gdpc.vector_tools import ivec3, ivec2, NORTH, WEST, SOUTH, EAST
from collections.abc import Iterator

from ..maps import Map
from ..styling.materials.material import MaterialParameterFunction
from ..styling.palette import Palette


# Class to work with grids for buildings
# Local coordinates are block coordinates relative to origin of house
# World coordinates are coordinates relative to world or editor origin
# Grid coordinates are cell coordinates, with dimensions according to the dimensions given
class Grid:
    def __init__(
        self,
        dimensions: ivec3 = ivec3(7, 5, 7),
        origin: ivec3 = ivec3(0, 0, 0),
    ) -> None:
        self.width, self.height, self.depth = dimensions
        self.dimensions = dimensions
        self.origin = origin

    # Coordinates functions
    def grid_to_local(self, coordinates: ivec3) -> ivec3:
        return ivec3(
            x=coordinates.x * (self.dimensions.x - 1),
            y=coordinates.y * (self.dimensions.y - 1),
            z=coordinates.z * (self.dimensions.z - 1),
        )

    def grid_to_world(self, coordinates: ivec3) -> ivec3:
        return self.local_to_world(self.grid_to_local(coordinates))

    def local_to_world(self, coordinates: ivec3) -> ivec3:
        return coordinates + self.origin

    # If on the boundary of two tiles, it will prefer the right one
    def local_to_grid(self, coordinates: ivec3) -> ivec3:
        return ivec3(
            x=coordinates.x // (self.dimensions.x - 1),
            y=coordinates.y // (self.dimensions.y - 1),
            z=coordinates.z // (self.dimensions.z - 1),
        )

    def world_to_local(self, coordinates: ivec3) -> ivec3:
        return coordinates - self.origin

    # NOTE: Unused method
    def world_to_grid(self, coordinates: ivec3) -> ivec3:
        return self.local_to_grid(self.world_to_local(coordinates))

    # helper function to build things on grid
    def build(
        self,
        editor: Editor,
        asset: NBTAsset,
        palette: Palette,
        grid_coordinate: ivec3,
        facing: ivec3 | str | None = None,
        material_params_func: MaterialParameterFunction | None = None,
        build_map: Map | None = None,
    ):
        coords = self.grid_to_local(grid_coordinate) + self.origin

        if isinstance(facing, ivec3):
            if facing == NORTH:
                facing = legacy_directions.NORTH
            elif facing == EAST:
                facing = legacy_directions.EAST
            elif facing == SOUTH:
                facing = legacy_directions.SOUTH
            elif facing == WEST:
                facing = legacy_directions.WEST

        if facing is None or not hasattr(asset, "facing") or asset.facing == facing:
            return build_nbt(
                editor,
                asset,
                palette,
                Transformation(
                    offset=coords + ivec3(0, 0, 0),
                ),
                material_params_func=material_params_func,
                build_map=build_map,
            )

        if legacy_directions.RIGHT[asset.facing] == facing:
            return build_nbt(
                editor,
                asset,
                palette,
                Transformation(
                    offset=coords + ivec3(self.width - 1, 0, 0),
                    rotations=1,
                ),
                material_params_func=material_params_func,
                build_map=build_map,
            )

        if legacy_directions.LEFT[asset.facing] == facing:
            return build_nbt(
                editor,
                asset,
                palette,
                Transformation(
                    offset=coords + ivec3(0, 0, self.depth - 1),
                    rotations=3,
                ),
                material_params_func=material_params_func,
                build_map=build_map,
            )

        if legacy_directions.OPPOSITES[asset.facing] == facing:
            return build_nbt(
                editor,
                asset,
                palette,
                Transformation(
                    offset=coords + ivec3(self.width - 1, 0, self.depth - 1),
                    rotations=2,
                ),
                material_params_func=material_params_func,
                build_map=build_map,
            )

    def get_points_at(self, point: ivec3) -> Iterator[ivec3]:
        for x in range(self.dimensions.x):
            for y in range(self.dimensions.y):
                for z in range(self.dimensions.z):
                    yield ivec3(x, y, z) + self.grid_to_world(point)

    def get_points_at_2d(self, point: ivec2) -> Iterator[ivec2]:
        dx, _, dz = self.grid_to_world(ivec3(point.x, 0, point.y))

        for x in range(self.dimensions.x):
            for z in range(self.dimensions.z):
                yield ivec2(x, z) + ivec2(dx, dz)
