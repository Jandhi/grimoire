from structures.nbt.convert_nbt import convert_nbt
from structures.nbt.nbt_asset import NBTAsset
from structures.structure import Structure
from structures.transformation import Transformation
from gdpc.editor import Editor
from gdpc.block import Block
from palette.palette import Palette
from palette.palette_swap import palette_swap

# Constructs an NBTAsset given an editor and transformation
def build_nbt(
        editor : Editor, 
        asset : NBTAsset,
        palette : Palette = None,
        transformation : Transformation = None,
        place_air : bool = False,
    ):
    structure = convert_nbt(asset.filepath)
    transformation = transformation or Transformation() # construct default value

    transformed_palette = transformation.apply_to_palette(structure.palette)

    for (pos, palette_index) in structure.blocks.items():
        block = transformed_palette[palette_index]

        if block.name in asset.do_not_place or block.name.removeprefix('minecraft:') in asset.do_not_place:
            continue

        if block.name == 'minecraft:air' and not place_air:
            continue

        if asset.palette:
            block = block.copy() # I do this to avoid doubly swapping palettes
            block.name = palette_swap(block.name, asset.palette, palette)

        x, y, z = transformation.apply_to_point(
            point=pos,
            structure=structure,
            asset=asset
        )

        editor.placeBlock(position=(x, y, z), block=block.to_gdpc_block()) 

