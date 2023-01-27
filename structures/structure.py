from structures.block import Block

# A class derived from an NBT file, data describing something built in minecraft
# Used to actually construct NBT structures
class Structure:
    def __init__(self, 
        blocks : dict[tuple[int, int, int], int], 
        palette : list[Block],
        dimensions : tuple[int, int, int],
    ) -> None:
        self.blocks = blocks
        self.palette = palette
        self.width, self.height, self.depth = dimensions

        
        
