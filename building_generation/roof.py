from structures.nbt_asset import NBTAsset

class Roof(NBTAsset):
    shape : list[tuple[int, int, int]]

    def on_construct(self):
        super().on_construct()
        self.shape = [tuple(*item) for item in self.shape]