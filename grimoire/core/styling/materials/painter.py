from typing import Callable, Self

from gdpc import Editor
from glm import ivec3

from grimoire.core.styling.blockform import BlockForm
from grimoire.core.styling.materials.material import Material, MaterialFeature
from grimoire.core.styling.materials.placer import Placer
from grimoire.core.styling.materials.traversal import MaterialTraversalStrategy


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
