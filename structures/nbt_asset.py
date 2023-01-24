class NBTAsset:
    name : str
    type : str
    nbt_path : str
    origin : tuple[int, int, int]

    def construct(self): # Called after fields are loaded in
        self.origin = tuple(self.origin) # convert list to tuple
