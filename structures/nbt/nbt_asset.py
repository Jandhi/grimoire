from data.asset import Asset, asset_defaults

# Base class with metadata for an NBT file
# We will be subclassing this for different types of structures, e.g. walls and rooms
@asset_defaults(do_not_replace = [], replace = [])
class NBTAsset(Asset):
    # The identifier for the jsons to know what NBTAsset this is
    # By default it is the snake case of the class name. 
    # It can be overridden such as here, since n_b_t_asset is silly.
    type_name = 'nbtasset' 

    filepath : str
    origin : tuple[int, int, int]
    do_not_replace : list[str] # blocks that should not be swapped by palette swapper
    replace : dict[str, str]   # blocks that must be swapped out