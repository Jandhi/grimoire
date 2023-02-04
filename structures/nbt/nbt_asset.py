from utils.strings import camel_to_snake_case

# Metaclass that registers NBTAsset subtypes
class NBTAssetMeta(type):
    def __new__(cls, name, bases, dct):
        subclass = super().__new__(cls, name, bases, dct)
        
        if subclass.__name__ != 'NBTAsset':
            NBTAsset.types.append(subclass)

            # See NBTAsset.type_name 
            if subclass.type_name == 'NBTAsset':
                subclass.type_name = camel_to_snake_case(subclass.__name__)

            NBTAsset.assets_by_type[subclass.type_name] = []
        else:
            subclass.types.append(subclass)
            subclass.assets_by_type['NBTAsset'] = []

        return subclass

# Error used for loading in NBT assets
class NBTAssetError(ValueError):
    def __init__(self, message : str) -> None:
        self.message =  message

# Decorator that allows for defaults to be set for certain values before validate is called
# Try to make them pass-by-value types. I'll copy lists and dicts, but you'll have problems otherwise.
def nbt_defaults(**kwargs):

    # Outer function binds the arguments for the inner function
    def modify_class(cls):
        old_validate = cls.validate

        def new_validate(ref):
            for field_name, field_value in kwargs.items():
                value = field_value

                if isinstance(value, list) or isinstance(value, dict):
                    value = value.copy()

                if not hasattr(ref, field_name):
                    setattr(ref, field_name, value)

            old_validate(ref)

        cls.validate = new_validate

        return cls

    return modify_class

# Base class with metadata for an NBT file
# We will be subclassing this for different types of structures, e.g. walls and rooms
@nbt_defaults(do_not_replace = [], replace = [])
class NBTAsset(metaclass=NBTAssetMeta):
    
    # The identifier for the jsons to know what NBTAsset this is
    # By default it is the snake case of the class name. 
    # It can be overridden such as here, since n_b_t_asset is silly.
    type_name = 'NBTAsset' 

    # Used to store loaded NBTS by type
    assets_by_type : dict[str, list] = {}

    # Object Fields
    name : str
    type : str
    filepath : str
    origin : tuple[int, int, int]
    do_not_replace : list[str] # blocks that should not be swapped by palette swapper
    replace : dict[str, str]   # blocks that must be swapped out
    types : list = []

    def __init__(self) -> None:
        NBTAsset.assets_by_type[type(self).type_name].append(self)


    # Called after fields are loaded in 
    # This function
    def validate(self):
        types = [type(self), *type(self).__bases__]

        for tp in types:
            for field_name in tp.__annotations__:
                if not hasattr(self, field_name):
                    NBTAsset.assets_by_type[type(self).type_name].remove(self)
                    raise NBTAssetError(f'Required field "{field_name}" ({tp.__annotations__[field_name].__name__}) not present in {self}')
    
    def on_construct(self): # Called after fields are validated
        self.origin = tuple(self.origin) # convert list to tuple
        
    @classmethod
    def new(cls, name, type, filepath, origin):
        obj = NBTAsset()
        obj.name = name
        obj.type = type
        obj.filepath = filepath
        obj.origin = origin
        return obj

    @classmethod
    def find_type(cls, name):
        for tp in NBTAsset.types:
            if tp.type_name == name:
                return tp

    @classmethod
    def all(cls):
        return NBTAsset.assets_by_type[cls.type_name]

    @classmethod
    def construct(cls, **kwargs):
        obj = cls()

        for key, val in kwargs.items():
            obj.__setattr__(key, val)
        
        obj.validate()
        obj.on_construct()

        return obj