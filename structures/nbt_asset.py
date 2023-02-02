# Base class with metadata for an NBT file
# We will be subclassing this for different types of structures, e.g. walls and rooms
class NBTAsset:
    name : str
    type : str
    filepath : str
    origin : tuple[int, int, int]
    do_not_replace : list[str] # blocks that should not be swapped by palette swapper

    def on_construct(self): # Called after fields are loaded in
        self.origin = tuple(self.origin) # convert list to tuple
        self.do_not_replace = self.do_not_replace or [] 

    @classmethod
    def new(cls, name, type, filepath, origin):
        obj = NBTAsset()
        obj.name = name
        obj.type = type
        obj.filepath = filepath
        obj.origin = origin
        return obj