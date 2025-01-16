from gdpc import Editor, Block
from gdpc.vector_tools import line2D, addY, dropY, length, circle
from glm import ivec3, ivec2

from grimoire.core.generator.generator_module import GeneratorModule
from grimoire.core.maps import Map
from grimoire.core.styling.blockform import BlockForm
from grimoire.core.styling.materials.gradient import (
    Gradient,
    PerlinSettings,
    GradientAxis,
)
from grimoire.core.styling.materials.material import MaterialFeature
from grimoire.core.styling.materials.painter import PalettePainter
from grimoire.core.styling.palette import Palette, MaterialRole
from grimoire.core.utils.bounds import clamp
from grimoire.core.utils.remap import remap_threshold_high
from grimoire.core.utils.sets.set_operations import find_edges, find_outline
from grimoire.core.utils.vectors import normalize_to_length


class BridgeBuilder(GeneratorModule):

    def __init__(
        self,
        parent: GeneratorModule,
        editor: Editor,
        build_map: Map,
        palette: Palette,
        start: ivec3,
        end: ivec3,
        height: int,
        width: int = 3,
        thickness: int = 1,
        length_per_support: int = -1,
        wood_floor: bool = False,
    ):
        super().__init__(parent)
        self.editor = editor
        self.palette = palette

        # Start should be equal to or higher than end
        if start.y < end.y:
            start, end = end, start

        self.start = start
        self.end = end
        self.height = height
        self.diff = self.end - self.start
        self.width = width
        self.thickness = thickness
        self.build_map = build_map
        self.length_per_support = length_per_support
        self.wood_floor = wood_floor

        self.intersection_length = self.find_intersection_length()
        # This is the value that the end point is as percent of the arc, where 1.0 is the intersection point
        #   where y == start.y
        # Note: this is usually greater than 1.0
        self.end_percent_of_intersection = length(
            dropY(self.end) - dropY(self.start)
        ) / (self.intersection_length * length(dropY(self.diff)))

    @GeneratorModule.main
    def build_bridge(self):

        line = line2D(
            dropY(self.start),
            dropY(self.end),
            width=self.width,
        )
        points = set(line)

        edge = (
            {}
            if self.width < 3
            else set(
                filter(
                    lambda p: not self.point_is_close_to_end(p),
                    find_edges(points, True),
                )
            )
        )

        moisture_func = remap_threshold_high(
            Gradient(13, self.build_map, 0.6, PerlinSettings(20, 8, 2))
            .with_axis(GradientAxis.y(self.end.y, self.start.y + self.height + 3, True))
            .to_func(),
            0.3,
        )

        wear_func = remap_threshold_high(
            Gradient(17, self.build_map, 0.8, PerlinSettings(40, 8, 2))
            .with_axis(GradientAxis.y(self.end.y, self.start.y + self.height + 3, True))
            .to_func(),
            0.3,
        )

        placer = (
            PalettePainter(self.editor, self.palette)
            .with_feature(MaterialFeature.MOISTURE, moisture_func)
            .with_feature(MaterialFeature.WEAR, wear_func)
        )

        for point in points:
            height = self.get_height_at(point)
            decimal = height - int(height)
            y = int(height) + self.start.y

            for i in range(5):
                self.editor.placeBlock(addY(point, y + i), Block("air"))

            for layer_y in range(self.thickness - 1):
                # Don't build below the ground
                if (
                    not self.build_map.is_in_bounds2d(point)
                    or self.build_map.ocean_floor_at(point) > y - layer_y
                ):
                    continue

                placer.place_block(
                    addY(point, y - layer_y),
                    MaterialRole.PRIMARY_STONE,
                    BlockForm.BLOCK,
                )

            if 0.25 < decimal <= 0.75:
                if point not in edge:
                    placer.place_block(
                        addY(point, y + 1),
                        (
                            MaterialRole.SECONDARY_WOOD
                            if self.wood_floor
                            else MaterialRole.PRIMARY_STONE
                        ),
                        BlockForm.SLAB,
                        {"type": "bottom"},
                    )
                else:
                    placer.place_block(
                        addY(point, y + 1),
                        MaterialRole.PRIMARY_STONE,
                        BlockForm.BLOCK,
                    )
                    placer.place_block(
                        addY(point, y + 2),
                        MaterialRole.PRIMARY_STONE,
                        BlockForm.WALL,
                    )
            elif decimal > 0.75:

                if point in edge:
                    placer.place_block(
                        addY(point, y + 1),
                        MaterialRole.PRIMARY_STONE,
                        BlockForm.BLOCK,
                    )

                    placer.place_block(
                        addY(point, y + 2),
                        MaterialRole.PRIMARY_STONE,
                        BlockForm.WALL,
                    )
                else:
                    placer.place_block(
                        addY(point, y + 1),
                        (
                            MaterialRole.SECONDARY_WOOD
                            if self.wood_floor
                            else MaterialRole.PRIMARY_STONE
                        ),
                        BlockForm.BLOCK,
                    )
            else:
                if point in edge:
                    placer.place_block(
                        addY(point, y),
                        MaterialRole.PRIMARY_STONE,
                        BlockForm.BLOCK,
                    )

                    placer.place_block(
                        addY(point, y + 1),
                        MaterialRole.PRIMARY_STONE,
                        BlockForm.WALL,
                    )
                else:
                    placer.place_block(
                        addY(point, y),
                        (
                            MaterialRole.SECONDARY_WOOD
                            if self.wood_floor
                            else MaterialRole.PRIMARY_STONE
                        ),
                        BlockForm.BLOCK,
                    )

        self.add_supports(points, placer)

    def add_supports(self, bridge_points: set[ivec2], placer: PalettePainter):
        if self.length_per_support == -1:
            return

        num_supports = int(length(dropY(self.diff)) / self.length_per_support)

        for i in range(num_supports):
            self.build_support(
                dropY(self.start)
                + normalize_to_length(
                    dropY(self.diff),
                    int((i + 1) * length(dropY(self.diff)) / (num_supports + 1)),
                ),
                bridge_points,
                placer,
            )

    def build_support(
        self, point: ivec2, bridge_points: set[ivec2], placer: PalettePainter
    ):
        diameter = int(
            max(1, self.width - 2 + ((self.width + 1) % 2))
        )  # We need to make sure it is odd!
        bottom = self.build_map.ocean_floor_at(point)
        top = self.start.y + int(self.get_height_at(point)) + 2 - self.thickness
        disk = set(circle((0, 0), diameter, True))
        disk_outline = find_outline(disk, 1)

        for y in range(bottom, top):
            for pt in disk:
                # Don't over place
                if self.start.y + int(self.get_height_at(pt + point)) < y:
                    continue

                # Decorative Layering
                if (self.start.y + y) % 8 == 0:
                    placer.place_block(
                        addY(pt + point, y),
                        MaterialRole.SECONDARY_STONE,
                        BlockForm.BLOCK,
                    )
                    continue

                placer.place_block(
                    addY(pt + point, y), MaterialRole.PRIMARY_STONE, BlockForm.BLOCK
                )

        # Widen at the top and bottom
        if top - bottom > 5 and diameter < self.width:
            for y in range(
                top - 5, top + 3
            ):  # We head higher so that if the bridge curves up, we still place
                for pt in disk_outline:
                    # Don't build past the edge of the bridge
                    if pt + point not in bridge_points:
                        continue

                    # Don't over place
                    if self.start.y + int(self.get_height_at(pt + point)) < y:
                        continue

                    # Decorative Layering
                    if (self.start.y + y) % 8 == 0:
                        placer.place_block(
                            addY(pt + point, y),
                            MaterialRole.SECONDARY_STONE,
                            BlockForm.BLOCK,
                        )
                        continue

                    placer.place_block(
                        addY(pt + point, y),
                        MaterialRole.PRIMARY_STONE,
                        BlockForm.BLOCK,
                    )

        if top - bottom > 15 and diameter < self.width:
            for pt in disk_outline:
                # Don't build past the edge of the bridge
                if pt + point not in bridge_points:
                    continue

                if not self.build_map.is_in_bounds2d(pt + point):
                    continue

                for y in range(
                    self.build_map.ocean_floor_at(pt + point),
                    self.build_map.height_at(point) + 3,
                ):  # Note that it goes up to the center point's height + 3, plus we thicken in water

                    # Decorative Layering
                    if (self.start.y + y) % 8 == 0:
                        placer.place_block(
                            addY(pt + point, y),
                            MaterialRole.SECONDARY_STONE,
                            BlockForm.BLOCK,
                        )
                        continue

                    placer.place_block(
                        addY(pt + point, y),
                        MaterialRole.PRIMARY_STONE,
                        BlockForm.BLOCK,
                    )

    def point_is_close_to_end(self, point: ivec2):
        return (
            length(dropY(self.start) - point) <= self.width // 2 + 1
            or length(dropY(self.end) - point) <= self.width // 2 + 1
        )

    # This is the percent length at which the bridge's y axis is equal to the start
    # If the start and end are level, this will be the end of the bridge
    def find_intersection_length(self) -> ivec3:

        # Coefficients for the quadratic equation
        a = 1
        b = -1
        c = self.diff.y / (self.height * 4)

        # Calculate the discriminant
        discriminant = b**2 - 4 * a * c

        if discriminant < 0:
            raise ValueError("No real solutions")

        # Calculate the two solutions using the quadratic formula
        d1 = (1 + discriminant**0.5) / 2
        d2 = (1 - discriminant**0.5) / 2

        return 1 / max(d1, d2)

    def get_height_at(self, point: ivec2):
        percent_distance = length(point - dropY(self.start)) / (
            self.intersection_length * length(dropY(self.diff))
        )

        # We do not allow the bridge to curve past the end or start
        percent_distance = clamp(percent_distance, 0, self.end_percent_of_intersection)

        return self.height * 4 * percent_distance * (1 - percent_distance)
