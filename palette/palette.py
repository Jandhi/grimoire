from core.assets.asset import Asset, asset_defaults


@asset_defaults(
    primary_wood="oak",
    secondary_wood="spruce",
    primary_stone="cobblestone",
    primary_stone_accent="stone_brick",
)
class Palette(Asset):
    primary_wood: str  # FIXME: Unused variable
    secondary_wood: str
    primary_stone: str
    primary_stone_accent: str  # FIXME: Unused variable

    fields = ["primary_wood", "secondary_wood", "primary_stone", "primary_stone_accent"]
