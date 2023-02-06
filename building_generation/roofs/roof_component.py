from structures.nbt.nbt_asset import NBTAsset

# Roof Component Types
SIDE = "side"
OUTSIDE_CORNER = "outside_corner"
INNER_CORNER = "inner_corner"
HALF = "half"

class RoofComponent(NBTAsset):
    component_type : str

    def on_construct(self):
        super().on_construct()