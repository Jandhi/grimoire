from structures.block import Block
from structures.directions import x_plus, x_minus, y_plus, y_minus, z_plus, z_minus, from_text, to_text, directions

# Transformation dictionaries
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

# Class
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
    def apply_to_text(self, text : str):
        direction = from_text(text)

        # For each dimensinos
        for dim in range(3):
            if self.mirror[dim]:
                direction = mirror_dicts[dim][direction]
        
        if self.diagonal_mirror:
            direction = diagonal_mirror[direction]
        
        return to_text(direction)

    def apply(self, block : Block):
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