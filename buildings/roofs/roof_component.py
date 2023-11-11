from structures.nbt.nbt_asset import NBTAsset
from core.assets.asset import asset_defaults
from structures.legacy_directions import x_minus

# Roof Component Types
SIDE = "side"
CORNER = "corner"
INNER = "inner" # inner corner

UPPER_SIDE = "upper_side"
UPPER_CORNER = "upper_corner"
UPPER_INNER = "upper_inner"

@asset_defaults(facing=x_minus)
class RoofComponent(NBTAsset):
    shape : str
    facing : str

    def on_construct(self):
        super().on_construct()