from typing import Self
import abc
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable

from gdpc import Editor, Block
from glm import ivec3

from grimoire.core.assets.asset import Asset, asset_defaults, default_subtype
from grimoire.core.noise.hash import recursive_hash, hash_string
from grimoire.core.noise.seed import Seed
from grimoire.core.styling.blockform import BlockForm
from grimoire.core.utils.strings import trim_minecraft_namespace
import grimoire.core.styling.materials.traversal as traversal


class MaterialFeature(Enum):
    SHADE = auto()
    WEAR = auto()
    MOISTURE = auto()
    DECORATION = auto()


FEATURE_TRAVERSAL_ORDER = [
    MaterialFeature.DECORATION,
    MaterialFeature.WEAR,
    MaterialFeature.MOISTURE,
    MaterialFeature.SHADE,
]


CALCULATE_RANGE = -1


@asset_defaults(
    feature_ranges={},
)
class Material(Asset):
    # Range
    # this refers to the amount of gradation that exists for a parameter
    feature_ranges: dict[MaterialFeature, tuple[int, int]]

    # Each connection is to a pair of materials representing a lower and higher amount of the feature
    connections: dict[MaterialFeature, tuple[Self | None, Self | None]]

    # BLOCK TYPES
    blocks: dict[BlockForm, str]

    # After the materials are linked, we want to calculate the range for each feature
    def on_link(self) -> None:
        if self.feature_ranges is None:
            self.feature_ranges = {}

        replacements: list[tuple[MaterialFeature, Material | None, Material | None]] = (
            []
        )

        for feature, pair in self.connections.items():
            # If the feature range is already set, no need to calculate it
            if feature in self.feature_ranges:
                continue

            less, more = pair

            less_depth = 0
            while less is not None:
                less_depth += 1
                less = less.with_less(feature)

            more_depth = 0
            while more is not None:
                more_depth += 1
                more = more.with_more(feature)

            self.feature_ranges[feature] = (less_depth, more_depth)

    def get_range(self, feature: MaterialFeature) -> tuple[int, int]:
        if feature not in self.feature_ranges:
            return 0, 0

        return self.feature_ranges[feature]

    # Returns the material with less of a feature, or none if it does not exist
    def with_less(self, feature: MaterialFeature) -> Self | None:
        if feature not in self.connections:
            return None

        return self.connections[feature][0]

    # Returns the material with more of a feature, or none if it does not exist
    def with_more(self, feature: MaterialFeature) -> Self | None:
        if feature not in self.connections:
            return None

        return self.connections[feature][1]

    def place_block(
        self,
        editor: Editor,
        form: BlockForm,
        position: ivec3,
        states: dict[str, str] = None,
        data: str | None = None,
        parameters: dict[MaterialFeature, float] = None,
        traversal_strategies: dict[
            MaterialFeature, traversal.MaterialTraversalStrategy
        ] = None,
    ):
        block_id = self.get_id(form, parameters, traversal_strategies)
        editor.placeBlock(
            position,
            Block(
                id=block_id,
                states=states or {},
                data=data,
            ),
        )

    def traverse(
        self,
        parameters: dict[MaterialFeature, float] | None,
        traversal_strategies: (
            dict[MaterialFeature, traversal.MaterialTraversalStrategy] | None
        ),
    ) -> Self:
        material = self
        parameters = parameters or {}
        traversal_strategies = traversal_strategies or {}

        for feature in FEATURE_TRAVERSAL_ORDER:
            if feature not in parameters:  # Feature will not be considered
                continue

            movement = traversal_strategies[feature].calculate_movements(
                material, feature, parameters[feature]
            )

            while movement > 0:
                material = material.connections[feature][1]
                movement -= 1
            while movement < 0:
                material = material.connections[feature][0]
                movement += 1

        return material

    def has_block(self, block: Block) -> bool:
        return trim_minecraft_namespace(block.id) in self.blocks.values()

    def has_form(self, form: BlockForm) -> bool:
        return form in self.blocks.keys()

    def get_id(
        self,
        form: BlockForm,
        parameters: dict[MaterialFeature, float] | None,
        traversal_strategies: (
            dict[MaterialFeature, traversal.MaterialTraversalStrategy] | None
        ),
    ) -> str | None:
        material = self.traverse(parameters, traversal_strategies)

        return material.blocks[form] if form in material.blocks else None
