from structures.block import Block
from structures.directions import x_plus, x_minus, y_plus, y_minus, z_plus, z_minus, from_text, to_text, directions
from structures.structure import Structure
from structures.nbt_asset import NBTAsset
from utils.tuples import sub_tuples, add_tuples

#region Transformation dictionaries
x_mirror = {
    x_plus : x_minus,
    x_minus : x_plus,
    y_plus : y_plus,
    y_minus : y_minus,
    z_plus : z_plus,
    z_minus : z_minus,
}
y_mirror = {
    x_plus : x_plus,
    x_minus : x_minus,
    y_plus : y_minus,
    y_minus : y_plus,
    z_plus : z_plus,
    z_minus : z_minus,
}
z_mirror = {
    x_plus : x_plus,
    x_minus : x_minus,
    y_plus : y_plus,
    y_minus : y_minus,
    z_plus : z_minus,
    z_minus : z_plus,
}
mirror_dicts = (x_mirror, y_mirror, z_mirror)

diagonal_mirror = {
    x_plus : z_plus,
    x_minus : z_minus,
    y_plus : y_plus,
    y_minus : y_minus,
    z_plus : x_plus,
    z_minus : x_minus,
    'x' : 'z',
    'z' : 'x',
}
#endregion

# Class to house tranformations of structures, including mirroring and offsets
# Rotation is only supported by switching the x/z axis, in other words diagonal_mirror
class Transformation:
    def __init__(self,
        offset : tuple[int, int, int] = None,
        mirror : tuple[bool, bool, bool] = None,
        diagonal_mirror : bool = False,
    ) -> None:
        self.offset = offset or (0, 0, 0)
        self.mirror = mirror or (False, False, False)
        self.diagonal_mirror = diagonal_mirror
    
    # Expects text to be in targets
    def apply_to_text(self, text : str) -> str:
        direction = from_text(text)

        # For each dimensinos
        for dim in range(3):
            if self.mirror[dim]:
                direction = mirror_dicts[dim][direction]
        
        if self.diagonal_mirror:
            direction = diagonal_mirror[direction]
        
        return to_text(direction)

    def apply_to_palette(self, palette : list[Block]) -> list[Block]:
        return [self.apply_to_block(block) for block in palette]

    def apply_to_block(self, block : Block) -> Block:
        name = block.name
        properties = {}

        for pname, pvalue in block.properties.items():
            direction_names = [to_text(direction) for direction in directions]
            
            if pname in direction_names:
                properties[self.__apply_to_text(pname)] = pvalue
            elif pvalue in direction_names:
                properties[pname] = self.apply_to_text(pvalue)
            # For axes
            elif pvalue in ('x', 'z') and self.diagonal_mirror: 
                properties[pname] = {'x' : 'z', 'z' : 'x'}[pvalue]
            # For right and left
            elif pvalue in ('right', 'left') and self.mirror[2]:
                properties[pname] = {'right' : 'left', 'left' : 'right'}[pvalue]
            # Everything else
            else:
                properties[pname] = pvalue

        return Block(name, properties)

    def apply_to_point(
        self,
        point : tuple[int, int, int],
        structure : Structure,
        asset : NBTAsset, 
    ) -> tuple[int, int, int]:
        x, y, z = point
        origin_x, origin_y, origin_z = asset.origin

        # mirroring
        # for now we will not mirror the origin 
        if self.mirror[0]: # x mirror
            x = structure.width - 1 - x
            # origin_x = structure.width - 1 - origin_x
        if self.mirror[1]: # y mirror
            y = structure.height - 1 - y
            # origin_y = structure.height - 1 - origin_y
        if self.mirror[2]: # z mirror
            z = structure.depth - 1 - z
            # origin_z = structure.depth - 1 - origin_z

        # origin offset
        x, y, z = sub_tuples((x, y, z), (origin_x, origin_y, origin_z))

        # rotation(ish)
        if self.diagonal_mirror:
            x, z = z, x

        # translation
        x, y, z = add_tuples((x, y, z), self.offset)

        return x, y, z