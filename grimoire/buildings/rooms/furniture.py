from ...core.structures.nbt.nbt_asset import NBTAsset
from ...core.assets.asset import asset_defaults
from ...core.structures.legacy_directions import X_PLUS


@asset_defaults(facing=X_PLUS)
class Furniture(NBTAsset):
    length: int
    facing: str
