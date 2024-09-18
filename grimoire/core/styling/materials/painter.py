from typing import Callable, Self

from gdpc import Editor, Block
from glm import ivec3

from grimoire.core.styling.blockform import BlockForm
from grimoire.core.styling.materials.material import Material, MaterialFeature
from grimoire.core.styling.materials.placer import Placer
from grimoire.core.styling.materials.traversal import MaterialTraversalStrategy
from grimoire.core.styling.palette import Palette, MaterialRole


class Painter:
    placer: Placer
    material: Material

    def __init__(self, editor: Editor, material: Material):
        self.placer = Placer(editor)
        self.material = material

    def with_feature(
        self,
        feature: MaterialFeature,
        func: Callable[[ivec3], float],
        traversal_strategy: MaterialTraversalStrategy = MaterialTraversalStrategy.LINEAR,
    ) -> Self:
        self.placer.feature_functions[feature] = func
        self.placer.traversal_strategies[feature] = traversal_strategy
        return self

    def get_parameters(self, position: ivec3) -> dict[MaterialFeature, float]:
        params = {}
        for feature, func in self.placer.feature_functions.items():
            params[feature] = func(position)

        return params

    def place_block(
        self,
        position: ivec3,
        form: BlockForm = BlockForm.BLOCK,
        states: dict[str, str] | None = None,
        data: str | None = None,
    ):
        params = self.get_parameters(position)
        self.material.place_block(
            self.placer.editor,
            form,
            position,
            states,
            data,
            params,
            self.placer.traversal_strategies,
        )


# Used to place blocks from a palette
class PalettePainter:
    placer: Placer
    palette: Palette

    def __init__(self, editor: Editor, palette: Palette):
        self.placer = Placer(editor)
        self.palette = palette

    def with_feature(
        self,
        feature: MaterialFeature,
        func: Callable[[ivec3], float],
        traversal_strategy: MaterialTraversalStrategy = MaterialTraversalStrategy.LINEAR,
    ) -> Self:
        self.placer.feature_functions[feature] = func
        self.placer.traversal_strategies[feature] = traversal_strategy
        return self

    def get_parameters(self, position: ivec3) -> dict[MaterialFeature, float]:
        params = {}
        for feature, func in self.placer.feature_functions.items():
            params[feature] = func(position)

        return params

    def place_block(
        self,
        position: ivec3,
        role: MaterialRole,
        form: BlockForm = BlockForm.BLOCK,
        states: dict[str, str] | None = None,
        data: str | None = None,
    ):
        block_id = self.palette.find_block_id(
            form,
            role,
            self.placer.get_parameters(position),
            self.placer.get_traversal_strategies(),
        )
        self.placer.editor.placeBlock(position, Block(block_id, states, data))
