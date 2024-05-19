from gdpc import Editor
from gdpc.vector_tools import ivec3

from ...core.noise.rng import RNG
from ...core.structures.grid import Grid
from ...core.structures.legacy_directions import EAST, NORTH, SOUTH, UP, WEST
from ...core.structures.nbt.build_nbt import build_nbt_legacy
from ...core.structures.transformation import Transformation
from ...core.utils.vectors import y_ivec3
from ..building_plan import BuildingPlan
from .roof_component import CORNER, INNER, SIDE, RoofComponent


def build_roof(
    plan: BuildingPlan, editor: Editor, roofComponents: list[RoofComponent], seed: int
):
    grid: Grid = plan.grid
    rng = RNG(seed, "build_roof")

    def roof_is_shape(shape: str):
        return lambda roof: roof.shape == shape

    corners = list(filter(roof_is_shape(CORNER), roofComponents))
    inners = list(filter(roof_is_shape(INNER), roofComponents))
    sides = list(filter(roof_is_shape(SIDE), roofComponents))

    corner = rng.choose(corners)
    inner = rng.choose(inners)
    side = rng.choose(sides)

    # northwest
    for cell in plan.cells:
        if cell.has_neighbour(UP):
            continue

        coords = grid.grid_to_local(cell.position + y_ivec3(1)) + grid.origin

        # northwest
        if cell.has_neighbour(NORTH) and cell.has_neighbour(WEST):
            build_nbt_legacy(
                editor,
                inner,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(0, 0, 0),
                ),
            )
        elif not cell.has_neighbour(NORTH) and not cell.has_neighbour(WEST):
            build_nbt_legacy(
                editor,
                corner,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(0, 0, 0),
                ),
            )
        elif cell.has_neighbour(NORTH) and not cell.has_neighbour(WEST):
            build_nbt_legacy(
                editor,
                side,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(0, 0, grid.depth // 2),
                    mirror=(False, False, True),
                ),
            )
        else:
            build_nbt_legacy(
                editor,
                side,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(grid.width // 2, 0, 0),
                    mirror=(False, False, True),
                    diagonal_mirror=True,
                ),
            )

        # northeast
        if cell.has_neighbour(NORTH) and cell.has_neighbour(EAST):
            build_nbt_legacy(
                editor,
                inner,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(grid.width - 1, 0, 0),
                    mirror=(True, False, False),
                ),
            )
        elif not cell.has_neighbour(NORTH) and not cell.has_neighbour(EAST):
            build_nbt_legacy(
                editor,
                corner,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(grid.width - 1, 0, 0),
                    mirror=(True, False, False),
                ),
            )
        elif cell.has_neighbour(NORTH) and not cell.has_neighbour(EAST):
            build_nbt_legacy(
                editor,
                side,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(grid.width - 1, 0, grid.depth // 2),
                    mirror=(True, False, True),
                ),
            )
        else:
            build_nbt_legacy(
                editor,
                side,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(0 + grid.width // 2, 0, 0),
                    mirror=(False, False, False),
                    diagonal_mirror=True,
                ),
            )

        # southwest
        if cell.has_neighbour(SOUTH) and cell.has_neighbour(WEST):
            build_nbt_legacy(
                editor,
                inner,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(0, 0, grid.depth - 1),
                    mirror=(False, False, True),
                ),
            )
        elif not cell.has_neighbour(SOUTH) and not cell.has_neighbour(WEST):
            build_nbt_legacy(
                editor,
                corner,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(0, 0, grid.depth - 1),
                    mirror=(False, False, True),
                ),
            )
        elif cell.has_neighbour(SOUTH) and not cell.has_neighbour(WEST):
            build_nbt_legacy(
                editor,
                side,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(0, 0, grid.depth // 2),
                    mirror=(False, False, False),
                ),
            )
        else:
            build_nbt_legacy(
                editor,
                side,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(grid.width // 2, 0, grid.depth - 1),
                    mirror=(True, False, True),
                    diagonal_mirror=True,
                ),
            )

        # southeast
        if cell.has_neighbour(SOUTH) and cell.has_neighbour(EAST):
            build_nbt_legacy(
                editor,
                inner,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(grid.width - 1, 0, grid.depth - 1),
                    mirror=(True, False, True),
                ),
            )
        elif not cell.has_neighbour(SOUTH) and not cell.has_neighbour(EAST):
            build_nbt_legacy(
                editor,
                corner,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(grid.width - 1, 0, grid.depth - 1),
                    mirror=(True, False, True),
                ),
            )
        elif cell.has_neighbour(SOUTH) and not cell.has_neighbour(EAST):
            build_nbt_legacy(
                editor,
                side,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(grid.depth - 1, 0, grid.depth // 2),
                    mirror=(True, False, False),
                ),
            )
        else:
            build_nbt_legacy(
                editor,
                side,
                cell.plan.palette,
                Transformation(
                    offset=coords + ivec3(grid.width // 2, 0, grid.depth - 1),
                    mirror=(True, False, False),
                    diagonal_mirror=True,
                ),
            )

        # northeast
        build_nbt_legacy(
            editor,
            corner,
            cell.plan.palette,
            Transformation(
                offset=coords + ivec3(grid.width - 1, 0, 0), mirror=(True, False, False)
            ),
        )

        # southwest
        build_nbt_legacy(
            editor,
            corner,
            cell.plan.palette,
            Transformation(
                offset=coords + ivec3(0, 0, grid.depth - 1), mirror=(False, False, True)
            ),
        )

        # southeast
        build_nbt_legacy(
            editor,
            corner,
            cell.plan.palette,
            Transformation(
                offset=coords + ivec3(grid.width - 1, 0, grid.depth - 1),
                mirror=(True, False, True),
            ),
        )
