from structures.nbt.nbt_asset import NBTAsset

class AssetStructure(NBTAsset):
    size: str #small = 7x7, medium = 13x17, large = 25x34
    facing: str = None #east/west/south/north