from structures.convert_nbt import convert_nbt
from structures.nbt_asset import NBTAsset
from structures.structure import Structure
from structures.transformation import Transformation
from gdpc.interface import Interface
from utils.tuples import add_tuples, sub_tuples

def build_nbt(
        interface : Interface, 
        asset : NBTAsset, 
        transformation : Transformation = None,
        place_air : bool = False,
    ):
    structure = convert_nbt(asset.filepath)

    for (pos, palette_index) in structure.blocks.items():
        block = structure.palette[palette_index]

        if block.name == 'minecraft:air' and not place_air:
            continue

        x, y, z = transform_point(
            point=pos,
            structure=structure,
            asset=asset,
            transformation=transformation,
        )

        interface.placeBlock(x, y, z, str(block)) 

def transform_point(
    point : tuple[int, int, int],
    structure : Structure,
    asset : NBTAsset, 
    transformation : Transformation = None,
):
    x, y, z = point
    origin_x, origin_y, origin_z = asset.origin

    if transformation is None:
        return sub_tuples((x, y, z), (origin_x, origin_y, origin_z))

    # mirroring
    if transformation.mirror[0]: # x mirror
        x = structure.width - 1 - x
        origin_x = structure.width - 1 - origin_x
    if transformation.mirror[1]: # y mirror
        y = structure.height - 1 - y
        origin_y = structure.height - 1 - origin_y
    if transformation.mirror[2]: # z mirror
        z = structure.depth - 1 - z
        origin_z = structure.depth - 1 - origin_z

    # origin offset
    x, y, z = sub_tuples((x, y, z), (origin_x, origin_y, origin_z))

    # rotation
    if transformation.diagonal_mirror:
        x, z = z, x

    # translation
    x, y, z = add_tuples((x, y, z), transformation.offset)

    return x, y, z