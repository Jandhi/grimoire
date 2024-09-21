from ..building_plan import BuildingPlan
from ..legacycell import LegacyCell
from ...core.maps import Map
from ...core.structures.legacy_directions import CARDINAL, LegacyDirection, UP
from gdpc.editor import Editor
from glm import ivec3

from ...core.noise.global_seed import GlobalSeed
from ...core.noise.rng import RNG
from ...core.structures.grid import Grid
from ...core.styling.materials.gradient import Gradient, GradientAxis, PerlinSettings
from ..building_plan import BuildingPlan
from ..legacycell import LegacyCell
from .wall import LOWER, UPPER, Wall
from enum import StrEnum, auto

from ...core.styling.materials.material import MaterialFeature
from ...core.styling.materials.placer import Placer


class RoofRestrictionTag(StrEnum):
    NOT_ROOF = auto()
    ONLY_ROOF = auto()


def build_walls(
    plan: BuildingPlan, editor: Editor, walls: list[Wall], rng: RNG, build_map: Map
):

    shade_gradient = Gradient(
        GlobalSeed.get(),
        build_map,
        noise_settings=PerlinSettings(
            base_octaves=27, noise_layers=6, add_ratio=1.7, strength=0.2
        ),
    ).with_axis(
        GradientAxis.y(plan.grid.origin.y, plan.grid.origin.y + plan.grid.height * 2)
    )

    placer = Placer(editor).with_feature(
        MaterialFeature.SHADE, shade_gradient.to_func()
    )

    for cell in plan.cells:
        for direction in CARDINAL:
            if not cell.has_neighbour(direction):
                build_wall(
                    placer,
                    cell,
                    direction,
                    walls,
                    rng,
                )


def build_wall(
    placer: Placer,
    cell: LegacyCell,
    direction: LegacyDirection,
    walls: list[Wall],
    rng: RNG,
):
    has_door = cell.has_door(direction)

    def wall_is_eligible(wall: Wall):
        if wall.has_door != has_door:
            return False

        return bool(
            (cell.position.y != 0 or wall.has_position(LOWER))
            and (cell.position.y <= 0 or wall.has_position(UPPER))
            and (cell.has_neighbour(UP) or RoofRestrictionTag.NOT_ROOF not in wall.tags)
            and (
                not cell.has_neighbour(UP)
                or RoofRestrictionTag.ONLY_ROOF not in wall.tags
            )
        )

    eligible_walls: list[Wall] = list(filter(wall_is_eligible, walls))

    weighted_walls = {
        wall: wall.weight if wall.weight > 0 else 100 for wall in eligible_walls
    }

    wall: Wall = rng.choose_weighted(weighted_walls)
    grid: Grid = cell.plan.grid

    if wall is None:
        print("Could not find suitable wall, skipped")
        return

    placer.place_on_grid(grid, wall, cell.plan.palette, cell.position, direction)
