from structures.block import Block
from structures.types import vec3

# A class derived from an NBT file, data describing something built in minecraft
# Used to actually construct NBT structures
class Structure:
    def __init__(self, 
        blocks : dict[vec3, int], 
        palette : list[Block],
        dimensions : vec3,
    ) -> None:
        self.blocks = blocks
        self.palette = palette
        self.width, self.height, self.depth = dimensions

        
        
