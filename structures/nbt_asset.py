# Base class with metadata for an NBT file
# We will be subclassing this for different types of structures, e.g. walls and rooms
class NBTAsset:
    name : str
    type : str
    filepath : str
    origin : tuple[int, int, int]

    def construct(self): # Called after fields are loaded in
        self.origin = tuple(self.origin) # convert list to tuple

    @classmethod
    def new(cls, name, type, filepath, origin):
        obj = NBTAsset()
        obj.name = name
        obj.type = type
        obj.filepath = filepath
        obj.origin = origin
        return obj