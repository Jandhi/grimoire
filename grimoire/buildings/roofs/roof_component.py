from ...core.structures.nbt.nbt_asset import NBTAsset
from ...core.assets.asset import asset_defaults
from ...core.structures.legacy_directions import X_MINUS

# Roof Component Types
SIDE = "side"
CORNER = "corner"
INNER = "inner"  # inner corner

UPPER_SIDE = "upper_side"
UPPER_CORNER = "upper_corner"
UPPER_INNER = "upper_inner"


@asset_defaults(facing=X_MINUS)
class RoofComponent(NBTAsset):
    shape: str
    facing: str
