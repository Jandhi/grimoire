from enum import Enum, auto

from gdpc import Editor, Block
from gdpc.vector_tools import (
    CARDINALS_AND_DIAGONALS_3D,
    NORTH,
    EAST,
    rotate3D,
    SOUTH,
    WEST,
    dropY,
)
from glm import ivec3

from grimoire.buildings.building_plan import BuildingPlan
from grimoire.core.generator.generator_module import GeneratorModule
from grimoire.core.maps import Map
from grimoire.core.noise.rng import RNG
from grimoire.core.structures import legacy_directions
from grimoire.core.structures.grid import Grid
from grimoire.core.structures.nbt.nbt_asset import NBTAsset
from grimoire.core.styling.blockform import BlockForm
from grimoire.core.styling.materials.gradient import Gradient, GradientAxis
from grimoire.core.styling.materials.material import MaterialFeature
from grimoire.core.styling.materials.painter import Painter
from grimoire.core.styling.palette import Palette, MaterialRole


class StiltComponentType(Enum):
    EDGE = auto()
    STAIRS = auto()
    CORNER = auto()
    INNER = auto()
    FLOOR = auto()


class StiltComponent(NBTAsset):
    component_type: StiltComponentType
    facing: str


def build_stilt_frame(
    editor: Editor,
    rng: RNG,
    palette: Palette | None,
    building_plan: BuildingPlan,
    build_map: Map,
):
    grid = building_plan.grid
    building_shape = set(building_plan.shape)

    grid.origin += ivec3(0, 2, 0)

    points: set[ivec3] = set()
    house_footprint = {point for point in building_shape if point.y == 0}

    edges = []
    stairs = []
    corners = []
    inners = []
    floors = []

    groups = {
        StiltComponentType.EDGE: edges,
        StiltComponentType.STAIRS: stairs,
        StiltComponentType.CORNER: corners,
        StiltComponentType.INNER: inners,
        StiltComponentType.FLOOR: floors,
    }
    for stilt in StiltComponent.all():
        groups[stilt.component_type].append(stilt)

    for point in house_footprint:
        if point not in points:
            points.add(point + ivec3(0, -1, 0))

        for d in CARDINALS_AND_DIAGONALS_3D:
            if point + d not in points:
                points.add(point + d + ivec3(0, -1, 0))

    for point in points:
        placed = False

        # CORNERS
        for vec, name in (
            (NORTH, legacy_directions.NORTH),
            (EAST, legacy_directions.EAST),
            (SOUTH, legacy_directions.SOUTH),
            (WEST, legacy_directions.WEST),
        ):
            if point + vec not in points and point + rotate3D(vec, 1) not in points:
                grid.build(
                    editor,
                    rng.choose(corners),
                    palette,
                    point,
                    facing=name,
                    build_map=build_map,
                )
                placed = True
                break
        if placed:
            continue

        # EDGES
        for vec, name in (
            (NORTH, legacy_directions.NORTH),
            (EAST, legacy_directions.EAST),
            (SOUTH, legacy_directions.SOUTH),
            (WEST, legacy_directions.WEST),
        ):
            if point + vec not in points and all(
                point + rotate3D(vec, i) in points for i in range(1, 4)
            ):
                if name in building_plan.cell_map[point - vec + ivec3(0, 1, 0)].doors:
                    grid.build(
                        editor,
                        rng.choose(stairs),
                        palette,
                        point,
                        facing=name,
                        build_map=build_map,
                    )
                else:
                    grid.build(
                        editor,
                        rng.choose(edges),
                        palette,
                        point,
                        facing=name,
                        build_map=build_map,
                    )
                placed = True
                break
        if placed:
            continue

        for vec, name in (
            (NORTH, legacy_directions.NORTH),
            (EAST, legacy_directions.EAST),
            (SOUTH, legacy_directions.SOUTH),
            (WEST, legacy_directions.WEST),
        ):
            if point + vec + rotate3D(vec, 1) not in points:
                grid.build(
                    editor,
                    rng.choose(inners),
                    palette,
                    point,
                    facing=name,
                    build_map=build_map,
                )
                placed = True
                break
        if placed:
            continue

        if all(point + d in points for d in CARDINALS_AND_DIAGONALS_3D):
            grid.build(
                editor,
                rng.choose(floors),
                palette,
                point,
                facing=name,
                build_map=build_map,
            )
            continue

    grid.origin -= ivec3(0, 2, 0)


class StiltPlacer(GeneratorModule):
    def __init__(self, parent: GeneratorModule | None):
        super().__init__(parent)

    @GeneratorModule.main
    def place(self, editor: Editor, build_map: Map, position: ivec3, palette: Palette):
        min_y = build_map.ocean_floor_at(dropY(position)) - 3

        gradient = Gradient(self.rng.next(), build_map).with_axis(
            GradientAxis.y(min_y, position.y)
        )
        painter = Painter(editor, palette.materials[MaterialRole.PILLAR]).with_feature(
            MaterialFeature.SHADE, gradient.to_func()
        )

        for y in range(min_y, position.y + 1):
            pos = ivec3(position.x, y, position.z)
            painter.place_block(pos)
