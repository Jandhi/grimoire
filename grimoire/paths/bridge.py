from gdpc import Editor, Block
from gdpc.vector_tools import line2D, addY, dropY, length
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
from grimoire.core.utils.remap import remap_threshold_high
from grimoire.core.utils.sets.set_operations import find_edges, find_outline
from grimoire.core.utils.vectors import normalize_to_length


class BridgeBuilder(GeneratorModule):
    WALL_CUTOFF = -0.8  # Under this height, no walls are placed

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
    ):
        super().__init__(parent)
        self.editor = editor
        self.palette = palette
        self.start = start
        self.end = end
        self.height = height
        self.diff = end - start
        self.width = width
        self.build_map = build_map

        self.end.y = self.start.y
        self.diff.y = 0
        # assert self.start.y == self.end.y

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
            .with_axis(
                GradientAxis.y(self.start.y, self.start.y + self.height + 3, True)
            )
            .to_func(),
            0.3,
        )

        wear_func = remap_threshold_high(
            Gradient(17, self.build_map, 0.8, PerlinSettings(40, 8, 2))
            .with_axis(
                GradientAxis.y(self.start.y, self.start.y + self.height + 3, True)
            )
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

            if 0.25 < decimal <= 0.75:
                if point not in edge:
                    placer.place_block(
                        addY(point, y + 1),
                        MaterialRole.PRIMARY_STONE,
                        BlockForm.SLAB,
                        {"type": "bottom"},
                    )
                elif height > self.WALL_CUTOFF:
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
                placer.place_block(
                    addY(point, y + 1),
                    MaterialRole.PRIMARY_STONE,
                    BlockForm.BLOCK,
                )

                if point in edge and height > self.WALL_CUTOFF:
                    placer.place_block(
                        addY(point, y + 2),
                        MaterialRole.PRIMARY_STONE,
                        BlockForm.WALL,
                    )
            else:
                placer.place_block(
                    addY(point, y),
                    MaterialRole.PRIMARY_STONE,
                    BlockForm.BLOCK,
                )

                if point in edge and height > self.WALL_CUTOFF:
                    placer.place_block(
                        addY(point, y + 1),
                        MaterialRole.PRIMARY_STONE,
                        BlockForm.WALL,
                    )

    def point_is_close_to_end(self, point: ivec2):
        return (
            length(dropY(self.start) - point) <= self.width // 2 + 1
            or length(dropY(self.end) - point) <= self.width // 2 + 1
        )

    def get_height_at(self, point: ivec2):
        percent_distance = ((point.x - self.start.x) + (point.y - self.start.z)) / (
            self.diff.x + self.diff.z
        )
        return self.height * 4 * percent_distance * (1 - percent_distance)
