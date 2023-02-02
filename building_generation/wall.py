from structures.nbt_asset import NBTAsset

class Wall(NBTAsset):
    facing : str

    def on_construct(self):
        super().on_construct()