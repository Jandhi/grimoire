from typing import Callable

from gdpc import Block
from gdpc.editor import Editor
from gdpc.lookup import TRAPDOORS, DOORS, FENCES, WALLS, SLABS, STAIRS, BUTTONS
from gdpc.vector_tools import ivec3

from grimoire.core.styling.legacy_palette import LegacyPalette, palette_swap
from .convert_nbt import convert_nbt
from .convert_schem import convert_schem
from .nbt_asset import NBTAsset
from ..transformation import Transformation
from ...maps import Map
from ...styling.materials.material import MaterialFeature
from ...styling.materials.traversal import MaterialTraversalStrategy
from ...styling.palette import Palette, swap


class ParameterGenerator:
    def get_parameters(self, position: ivec3) -> dict[MaterialFeature, float]:
        pass

    def get_traversal_strategies(
        self,
    ) -> dict[MaterialFeature, MaterialTraversalStrategy]:
        pass


def build_nbt(
    editor: Editor,
    asset: NBTAsset,
    palette: Palette | None,
    transformation: Transformation = None,
    place_air: bool = False,
    allow_non_solid_replacement: bool = False,
    parameter_generator: ParameterGenerator | None = None,
    build_map: Map | None = None,  # Required for some submodule calls
):
    """Constructs an NBTAsset given an editor and transformation
    If given a palette, will palette swap using the structure's own palette and the given palette
    """
    structure = (
        convert_schem(asset.filepath)
        if asset.filepath.endswith(".schem")
        else convert_nbt(asset.filepath)
    )
    transformation = transformation or Transformation()  # construct default value

    transformed_palette = transformation.apply_to_palette(structure.palette)

    for pos, palette_index_and_nbt in structure.blocks.items():
        palette_index = palette_index_and_nbt[0]
        nbt = palette_index_and_nbt[1]
        block = transformed_palette[palette_index]

        if not block.id.startswith("minecraft"):
            block.id = f"minecraft:{block.id}"

        if block.id in asset.do_not_place or (
            block.id == "minecraft:air" and not place_air
        ):
            continue

        x, y, z = transformation.apply_to_point(point=pos, asset=asset)

        # don't swap if either are null
        if asset.palette and palette:
            block = Block(
                block.id, block.states.copy(), block.data
            )  # I do this to avoid doubly swapping palettes
            block = swap(
                block,
                asset.palette,
                palette,
                (
                    parameter_generator.get_parameters(ivec3(x, y, z))
                    if parameter_generator is not None
                    else {}
                ),
                (
                    parameter_generator.get_traversal_strategies()
                    if parameter_generator is not None
                    else {}
                ),
            )

        # Doesn't allow non-solid blocks to replace blocks
        if (not allow_non_solid_replacement) and any(
            blocktype in block.id
            for blocktype in STAIRS
            | SLABS
            | WALLS
            | FENCES
            | DOORS
            | TRAPDOORS
            | BUTTONS
        ):
            curr_block = editor.getBlock(position=(x, y, z))

            if "air" not in curr_block.id:
                continue

        if block.id == "minecraft:barrier":
            block.id = "minecraft:air"

        if block.id == "minecraft:structure_void":
            continue

        if nbt != None:
            block.data = nbt

        editor.placeBlock(position=(x, y, z), block=block)

    for pos, entity in structure.entities.items():
        id = entity[0]
        nbt = entity[1]

        x, y, z = transformation.apply_to_point(point=pos, asset=asset)
        summon_entity_command = f"summon {id} {x} {y} {z} {nbt}"
        editor.runCommand(summon_entity_command, position=ivec3(x, y, z))

    # RUN SUBMODULES
    for submodule in asset.submodules:
        submodule = submodule.clone()  # Clone so we don't overwrite the original object

        if "editor" in submodule.arguments:
            submodule.arguments["editor"] = editor
        if "build_map" in submodule.arguments:
            submodule.arguments["build_map"] = build_map
        if "palette" in submodule.arguments:
            submodule.arguments["palette"] = palette

        # TRANSFORM POINTS
        annotations: dict[str, type] = submodule.module._main.__annotations__
        for key, val in annotations.items():
            if val == ivec3:
                submodule.arguments[key] = transformation.apply_to_point(
                    submodule.arguments[key], asset
                )

        submodule.run()


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

        x, y, z = transformation.apply_to_point(point=pos, asset=asset)

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

        x, y, z = transformation.apply_to_point(point=pos, asset=asset)
        summon_entity_command = f"summon {id} {x} {y} {z} {nbt}"
        editor.runCommand(summon_entity_command, position=ivec3(x, y, z))
