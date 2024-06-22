from gdpc import Editor, Block
from gdpc.vector_tools import line2D, addY, dropY, length
from glm import ivec3, ivec2

from grimoire.core.generator.generator_module import GeneratorModule
from grimoire.core.styling.blockform import BlockForm
from grimoire.core.styling.materials.material import MaterialParameters
from grimoire.core.styling.palette import Palette, MaterialRole
from grimoire.core.utils.sets.set_operations import find_edges, find_outline
from grimoire.core.utils.vectors import normalize_to_length


class BridgeBuilder(GeneratorModule):
    WALL_CUTOFF = -0.8  # Under this height, no walls are placed

    def __init__(
        self,
        parent: GeneratorModule,
        editor: Editor,
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

        for point in points:
            height = self.get_height_at(point)
            decimal = height - int(height)
            y = int(height) + self.start.y

            if 0.25 < decimal <= 0.75:
                if point not in edge:
                    self.place_slab(addY(point, y))
                elif height > self.WALL_CUTOFF:
                    self.place_block(addY(point, y + 1))
                    self.place_wall(addY(point, y + 2))
            elif decimal > 0.75:
                self.place_block(addY(point, y + 1))

                if point in edge and height > self.WALL_CUTOFF:
                    self.place_wall(addY(point, y + 2))
            else:
                self.place_block(addY(point, y))

                if point in edge and height > self.WALL_CUTOFF:
                    self.place_wall(addY(point, y + 1))

    def point_is_close_to_end(self, point: ivec2):
        return (
            length(dropY(self.start) - point) <= self.width // 2 + 1
            or length(dropY(self.end) - point) <= self.width // 2 + 1
        )

    def place_block(self, point: ivec3):
        block_id = self.palette.find_block_id(
            BlockForm.BLOCK,
            MaterialParameters.default(point),
            MaterialRole.PRIMARY_STONE,
        )

        self.editor.placeBlock(point, Block(block_id))

    def place_slab(self, point: ivec3):
        block_id = self.palette.find_block_id(
            BlockForm.SLAB,
            MaterialParameters.default(point),
            MaterialRole.PRIMARY_STONE,
        )

        self.editor.placeBlock(point, Block(block_id, states={"type": "top"}))
        self.editor.placeBlock(point + ivec3(0, 1, 0), Block(block_id))

    def place_wall(self, point: ivec3):
        block_id = self.palette.find_block_id(
            BlockForm.WALL,
            MaterialParameters.default(point),
            MaterialRole.SECONDARY_STONE,
        )

        self.editor.placeBlock(point, Block(block_id))

    def get_height_at(self, point: ivec2):
        percent_distance = ((point.x - self.start.x) + (point.y - self.start.z)) / (
            self.diff.x + self.diff.z
        )
        return self.height * 4 * percent_distance * (1 - percent_distance)
