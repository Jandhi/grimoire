from gdpc import Block
from gdpc.editor import Editor
from gdpc.vector_tools import ivec3

from grimoire.core.styling.legacy_palette import LegacyPalette, palette_swap
from .convert_nbt import convert_nbt
from .nbt_asset import NBTAsset
from ..transformation import Transformation
from ...styling.palette import Palette


def build_nbt(
    editor,
    asset,
    palette: Palette,
):
    pass


# Constructs an NBTAsset given an editor and transformation
def build_nbt_legacy(
    editor: Editor,
    asset: NBTAsset,
    palette: LegacyPalette = None,
    transformation: Transformation = None,
    place_air: bool = False,
    allow_non_solid_replacement: bool = False,
):
    structure = convert_nbt(asset.filepath)
    transformation = transformation or Transformation()  # construct default value

    transformed_palette = transformation.apply_to_palette(structure.palette)

    for pos, palette_index_and_nbt in structure.blocks.items():
        palette_index = palette_index_and_nbt[0]
        nbt = palette_index_and_nbt[1]
        block = transformed_palette[palette_index]

        if (
            block.id in asset.do_not_place
            or block.id.removeprefix("minecraft:") in asset.do_not_place
        ):
            continue

        if block.id == "minecraft:air" and not place_air:
            continue

        # don't swap if either are null
        if asset.palette and palette:
            block = Block(
                block.id, block.states.copy(), block.data
            )  # I do this to avoid doubly swapping palettes
            block.id = palette_swap(block.id, asset.palette, palette)

        x, y, z = transformation.apply_to_point(
            point=pos, structure=structure, asset=asset
        )

        # Doesn't allow non-solid blocks to replace blocks
        if (not allow_non_solid_replacement) and any(
            blocktype in block.id for blocktype in ("stairs", "slab", "walls", "fence")
        ):
            curr_block = editor.getBlock(position=(x, y, z))

            if "air" not in curr_block.id:
                continue

        if block.id == "minecraft:barrier":
            block.id = "minecraft:air"

        editor.placeBlock(position=(x, y, z), block=block)

    for pos, entity in structure.entities.items():
        id = entity[0]
        nbt = entity[1]

        x, y, z = transformation.apply_to_point(
            point=pos, structure=structure, asset=asset
        )
        summon_entity_command = f"summon {id} {x} {y} {z} {nbt}"
        editor.runCommand(summon_entity_command, position=ivec3(x, y, z))
