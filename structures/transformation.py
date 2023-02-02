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
                properties[self.apply_to_text(pname)] = pvalue
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

        # mirroring
        # for now we will not mirror the origin 
        if self.mirror[0]: # x mirror
            x = -1 * x
        if self.mirror[2]: # z mirror
            z = -1 * z
        
        # rotation(ish)
        if self.diagonal_mirror:
            x, z = z, x

        # Shift according to origin
        origin = self.apply_to_origin(asset.origin)
        x, y, z = sub_tuples((x, y, z), origin)

        # translation
        x, y, z = add_tuples((x, y, z), self.offset)

        return x, y, z
    
    def apply_to_origin(
        self,
        point : tuple[int, int, int]
    ) -> tuple[int, int, int]:
        origin = point

        if self.mirror[0]: # x mirror
            origin = (-1 * origin[0], origin[1], origin[2])
        if self.mirror[2]: # z mirror
            origin = (origin[0], origin[1], -1 * origin[2])

        if self.diagonal_mirror:
            origin = (origin[2], origin[1], origin[0])

        return origin
