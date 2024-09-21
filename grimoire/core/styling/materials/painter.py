from typing import Callable, Self

from gdpc import Editor, Block
from glm import ivec3

from grimoire.core.maps import Map
from grimoire.core.structures.nbt.build_nbt import build_nbt, ParameterGenerator
from grimoire.core.structures.nbt.nbt_asset import NBTAsset
from grimoire.core.structures.transformation import Transformation
from grimoire.core.styling.blockform import BlockForm
from grimoire.core.styling.materials.material import Material, MaterialFeature
from grimoire.core.styling.materials.placer import Placer
from grimoire.core.styling.materials.traversal import MaterialTraversalStrategy
from grimoire.core.styling.palette import Palette, MaterialRole


class Painter(ParameterGenerator):
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

    def get_traversal_strategies(
        self,
    ) -> dict[MaterialFeature, MaterialTraversalStrategy]:
        return self.placer.get_traversal_strategies()

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
class PalettePainter(ParameterGenerator):
    placer: Placer
    palette: Palette

    def __init__(self, editor: Editor, palette: Palette):
        self.placer = Placer(editor)
        self.palette = palette

    def with_feature(
        self,
        feature: MaterialFeature,
        func: Callable[[ivec3], float],
        traversal_strategy: MaterialTraversalStrategy = MaterialTraversalStrategy.SCALED,
    ) -> Self:
        self.placer.feature_functions[feature] = func
        self.placer.traversal_strategies[feature] = traversal_strategy
        return self

    def get_parameters(self, position: ivec3) -> dict[MaterialFeature, float]:
        params = {}
        for feature, func in self.placer.feature_functions.items():
            params[feature] = func(position)

        return params

    def get_traversal_strategies(
        self,
    ) -> dict[MaterialFeature, MaterialTraversalStrategy]:
        return self.placer.get_traversal_strategies()

    def place_block(
        self,
        position: ivec3,
        role: MaterialRole,
        form: BlockForm = BlockForm.BLOCK,
        states: dict[str, str] | None = None,
        data: str | None = None,
    ):
        params = self.placer.get_parameters(position)

        block_id = self.palette.find_block_id(
            form,
            role,
            params,
            self.placer.get_traversal_strategies(),
        )
        self.placer.editor.placeBlock(position, Block(block_id, states or {}, data))

    def place_nbt(
        self,
        asset: NBTAsset,
        transformation: Transformation,
        place_air: bool = False,
        allow_non_solid_replacement: bool = False,
        build_map: Map | None = None,  # Required for some submodule calls
    ):
        build_nbt(
            self.placer.editor,
            asset,
            self.palette,
            transformation,
            place_air,
            allow_non_solid_replacement,
            self,
            build_map,
        )
