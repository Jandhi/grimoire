from structures.nbt_asset import NBTAsset

class Wall(NBTAsset):
    facing_direction : str

    def construct(self):
        return super().construct()