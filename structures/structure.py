from structures.block import Block
from gdpc.vector_tools import ivec3

# A class derived from an NBT file, data describing something built in minecraft
# Used to actually construct NBT structures
class Structure:
    def __init__(self, 
        blocks : dict[ivec3, int], 
        palette : list[Block],
        dimensions : ivec3,
    ) -> None:
        self.blocks = blocks
        self.palette = palette
        self.width, self.height, self.depth = dimensions

        
        
