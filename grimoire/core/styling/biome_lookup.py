from grimoire.core.styling.palette import Palette, BuildStyle


ARID_BIOMES = [
    "desert",
    "desert_hills",
    "savanna",
    "savanna_plateau",
    "windswept_savanna",
    "badlands",
    "wooded_badlands_plateau",
    "badlands_plateau",
    "desert_lakes",
    "shattered_savanna",
    "shattered_savanna_plateau",
    "eroded_badlands",
    "modified_wooded_badlands_plateau",
    "modified_badlands_plateau",
]

WET_BIOMES = [
    "ocean",
    "swamp",
    "river",
    "frozen_ocean",
    "frozen_river",
    "beach",
    "warm_ocean",
    "lukewarm_ocean",
    "cold_ocean",
    "deep_warm_ocean",
    "deep_lukewarm_ocean",
    "deep_cold_ocean",
    "deep_frozen_ocean",
    "swamp_hills",
    "jungle",
    "bamboo_jungle",
    "bamboo_jungle_hills",
    "cherry_grove",
]

SPRUCE_BIOMES = []

ACACIA_BIOMES = []


def get_style_and_palettes(biome: str) -> tuple[BuildStyle, list[Palette]]:
    biome = biome.removeprefix("minecraft:")
    style = BuildStyle.NORMAL_MEDIEVAL

    if biome in ARID_BIOMES:
        style = BuildStyle.DESERT
    if biome in WET_BIOMES:
        style = BuildStyle.WET

    palettes = [
        palette for palette in Palette.all() if style.name.lower() in palette.tags
    ]

    return style, palettes
