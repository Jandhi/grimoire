from structures.nbt.convert_nbt import convert_nbt
from structures.nbt.nbt_asset import NBTAsset
from structures.structure import Structure
from structures.transformation import Transformation
from gdpc.interface import Interface
from utils.tuples import add_tuples, sub_tuples

# Constructs an NBTAsset given an interface and transformation
def build_nbt(
        interface : Interface, 
        asset : NBTAsset, 
        transformation : Transformation = None,
        place_air : bool = False,
    ):
    structure = convert_nbt(asset.filepath)
    transformation = transformation or Transformation() # construct default value

    transformed_palette = transformation.apply_to_palette(structure.palette)

    for (pos, palette_index) in structure.blocks.items():
        block = transformed_palette[palette_index]

        if block.name == 'minecraft:air' and not place_air:
            continue

        x, y, z = transformation.apply_to_point(
            point=pos,
            structure=structure,
            asset=asset
        )

        interface.placeBlock(x, y, z, str(block)) 

