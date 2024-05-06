from dataclasses import dataclass
from enum import Enum
from typing import Union

from gdpc import Editor, Block
from glm import ivec3

from grimoire.core.assets.asset import Asset, asset_defaults, default_subtype
from grimoire.core.materials.dithering import (
    DitheringPattern,
    calculate_dither_regular,
    calculate_dither_random,
)
from grimoire.core.noise.global_seed import GlobalSeed
from grimoire.core.noise.rng import RNG


@dataclass
class MaterialParameters:
    position: ivec3

    # 0 for darkest, 1 for lightest
    shade: float

    # 0 for no age, 1 for oldest
    age: float

    # 0 for no moisture, 1 for most moisture
    moisture: float


class Material(Asset):
    dithering_pattern: DitheringPattern

    def build(
        self,
        editor: Editor,
        parameters: MaterialParameters,
        rng: RNG,
        dithering_pattern: DitheringPattern | None = None,
    ):
        pass


CALCULATE_RANGE = -1


@default_subtype(Material)
@asset_defaults(
    shade_range=CALCULATE_RANGE,
    age_range=CALCULATE_RANGE,
    moisture_range=CALCULATE_RANGE,
    lighter=None,
    darker=None,
    older=None,
    younger=None,
    more_moist=None,
    less_moist=None,
)
class BasicMaterial(Material):
    # Range
    # this refers to the amount of gradation that exists for a parameter
    # CALCULATE_RANGE means that the range will be determined at creation
    # for shade, this is determined by the maximum depth of lighter or darker
    # for age and moisture, this is determined by the depth of older and more_moist
    shade_range: int
    age_range: int
    moisture_range: int

    # CONNECTIONS
    # Shade
    lighter: Material | None
    darker: Material | None
    # Age
    older: Material | None
    younger: Material | None
    # Moisture:
    more_moist: Material | None
    less_moist: Material | None

    def on_link(self) -> None:
        # shade
        lighter_amt = 0
        root = self
        while root.lighter is not None:
            lighter_amt += 1
            root = root.lighter

            while isinstance(root, CompositeMaterial):
                root = list(root.submaterials.keys())[0]

        darker_amt = 0
        root = self
        while root.darker is not None:
            darker_amt += 1
            root = root.darker

            while isinstance(root, CompositeMaterial):
                root = list(root.submaterials.keys())[0]

        self.shade_range = 1 + 2 * min(lighter_amt, darker_amt)

        # age
        age_range = 1
        root = self
        while root.older is not None:
            age_range += 1
            root = root.older

            while isinstance(root, CompositeMaterial):
                root = list(root.submaterials.keys())[0]
        self.age_range = age_range

        # moisture
        moisture_range = 1
        root = self
        while root.more_moist is not None:
            moisture_range += 1
            root = root.more_moist

            while isinstance(root, CompositeMaterial):
                root = list(root.submaterials.keys())[0]
        self.moisture_range = moisture_range

    def build(
        self,
        editor: Editor,
        parameters: MaterialParameters,
        rng: RNG,
        dithering_pattern: DitheringPattern | None = None,
    ):
        material = self.traverse(
            parameters,
            rng,
            self.dithering_pattern if dithering_pattern is None else dithering_pattern,
        )
        block = Block(id=material.name)
        editor.placeBlock(parameters.position, block)

    def traverse(
        self, params: MaterialParameters, rng: RNG, dithering_pattern: DitheringPattern
    ) -> "BasicMaterial":
        shade_index = self.calculate_index(
            params.shade, self.shade_range, params.position, rng, dithering_pattern
        )
        material = self

        shade_diff = shade_index - int(self.shade_range / 2)
        if shade_diff > 0:
            # lighter
            for _ in range(shade_diff):
                if material.lighter is None:
                    break
                material = material.lighter
        elif shade_diff < 0:
            # darker
            for _ in range(-1 * shade_diff):
                if material.darker is None:
                    break
                material = material.darker

        age_index = self.calculate_index(
            params.age, self.age_range, params.position, rng, dithering_pattern
        )
        for _ in range(age_index):
            if material.older is None:
                break
            material = material.older

        moist_index = self.calculate_index(
            params.moisture,
            self.moisture_range,
            params.position,
            rng,
            dithering_pattern,
        )
        for _ in range(age_index):
            if material.more_moist is None:
                break
            material = material.more_moist

        return material

    def calculate_index(
        self,
        value: float,
        dimension_range: int,
        position: ivec3,
        rng: RNG,
        dithering_pattern: DitheringPattern,
    ) -> int:
        if dimension_range == 1:
            return 0

        return dithering_pattern.calculate_index(value, dimension_range, position, rng)


class CompositeMaterial(Material):
    submaterials: dict[Material, int]

    def random_submaterial(self, rng: RNG) -> Material:
        return rng.choose_weighted(self.submaterials)

    def build(
        self,
        editor: Editor,
        parameters: MaterialParameters,
        rng: RNG,
        dithering_pattern: DitheringPattern | None = None,
    ):
        return self.random_submaterial(rng).build(
            editor,
            parameters,
            rng,
            self.dithering_pattern if dithering_pattern is None else dithering_pattern,
        )


def calculate_shade():
    pass
