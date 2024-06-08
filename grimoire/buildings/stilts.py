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
from grimoire.core.generator.module import Module
from grimoire.core.maps import Map
from grimoire.core.noise.rng import RNG
from grimoire.core.structures.grid import Grid
from grimoire.core.structures.legacy_directions import north, west, south, east
from grimoire.core.structures.nbt.nbt_asset import NBTAsset
from grimoire.core.styling.blockform import BlockForm
from grimoire.core.styling.materials.dithering import DitheringPattern
from grimoire.core.styling.materials.gradient import Gradient, GradientAxis
from grimoire.core.styling.materials.material import MaterialParameters
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

    edges = [
        stilt
        for stilt in StiltComponent.all()
        if stilt.component_type == StiltComponentType.EDGE
    ]
    stairs = [
        stilt
        for stilt in StiltComponent.all()
        if stilt.component_type == StiltComponentType.STAIRS
    ]
    corners = [
        stilt
        for stilt in StiltComponent.all()
        if stilt.component_type == StiltComponentType.CORNER
    ]
    inners = [
        stilt
        for stilt in StiltComponent.all()
        if stilt.component_type == StiltComponentType.INNER
    ]
    floors = [
        stilt
        for stilt in StiltComponent.all()
        if stilt.component_type == StiltComponentType.FLOOR
    ]

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
            (NORTH, north),
            (EAST, east),
            (SOUTH, south),
            (WEST, west),
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
            (NORTH, north),
            (EAST, east),
            (SOUTH, south),
            (WEST, west),
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
            (NORTH, north),
            (EAST, east),
            (SOUTH, south),
            (WEST, west),
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


class StiltPlacer(Module):
    def __init__(self, parent: Module | None):
        super().__init__(parent)

    @Module.main
    def place(self, editor: Editor, build_map: Map, position: ivec3, palette: Palette):
        min_y = build_map.ocean_floor_at(dropY(position)) - 3

        gradient = Gradient(self.rng.next()).with_axis(
            GradientAxis.y(min_y, position.y)
        )

        for y in range(min_y, position.y + 1):
            pos = ivec3(position.x, y, position.z)

            id = (
                palette.find_block_id(
                    BlockForm.BLOCK,
                    MaterialParameters(
                        position=pos,
                        age=0,
                        moisture=0,  # TODO make it fit the water level
                        shade=gradient.calculate_gradient_value(pos),
                        dithering_pattern=DitheringPattern.RANDOM_EASE_CUBIC,
                    ),
                    MaterialRole.PILLAR,
                )
                if palette is not None
                else None or "oak_log"
            )

            editor.placeBlock(pos, Block(id))
