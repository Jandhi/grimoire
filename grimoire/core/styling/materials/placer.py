from typing import Callable, Self

from gdpc import Editor
from glm import ivec3

from grimoire.core.maps import Map
from grimoire.core.structures.grid import Grid
from grimoire.core.structures.nbt.build_nbt import ParameterGenerator, build_nbt
from grimoire.core.structures.nbt.nbt_asset import NBTAsset
from grimoire.core.structures.transformation import Transformation
from grimoire.core.styling.blockform import BlockForm
from grimoire.core.styling.materials.material import Material, MaterialFeature
from grimoire.core.styling.materials.traversal import MaterialTraversalStrategy
from grimoire.core.styling.palette import Palette


class Placer(ParameterGenerator):
    editor: Editor
    feature_functions: dict[MaterialFeature, Callable[[ivec3], float]]
    traversal_strategies: dict[MaterialFeature, MaterialTraversalStrategy]

    def __init__(self, editor: Editor):
        self.editor = editor
        self.feature_functions = {}
        self.traversal_strategies = {}

    def with_feature(
        self,
        feature: MaterialFeature,
        func: Callable[[ivec3], float],
        traversal_strategy: MaterialTraversalStrategy = MaterialTraversalStrategy.LINEAR,
    ) -> Self:
        self.feature_functions[feature] = func
        self.traversal_strategies[feature] = traversal_strategy
        return self

    def get_parameters(self, position: ivec3) -> dict[MaterialFeature, float]:
        params = {}
        for feature, func in self.feature_functions.items():
            params[feature] = func(position)

        return params

    def get_traversal_strategies(
        self,
    ) -> dict[MaterialFeature, MaterialTraversalStrategy]:
        return self.traversal_strategies

    def place_nbt(
        self,
        asset: NBTAsset,
        palette: Palette | None,
        transformation: Transformation = None,
        place_air: bool = False,
        allow_non_solid_replacement: bool = False,
        build_map: Map | None = None,  # Required for some submodule calls
    ):
        build_nbt(
            self.editor,
            asset,
            palette,
            transformation,
            place_air,
            allow_non_solid_replacement,
            self,
            build_map,
        )

    def place_block(
        self,
        material: Material,
        form: BlockForm,
        position: ivec3,
        states: dict[str, str] | None = None,
        data: str | None = None,
    ):
        params = self.get_parameters(position)
        material.place_block(
            self.editor, form, position, states, data, params, self.traversal_strategies
        )

    def place_on_grid(
        self,
        grid: Grid,
        asset: NBTAsset,
        palette: Palette,
        grid_coordinate: ivec3,
        facing: ivec3 | str | None = None,
        build_map: Map | None = None,
    ):
        grid.build(
            self.editor, asset, palette, grid_coordinate, facing, self, build_map
        )
