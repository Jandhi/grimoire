from structures.block import Block

class Structure:
    def __init__(self, blocks : dict[tuple[int, int, int], int], palette : list[Block]) -> None:
        self.blocks = blocks
        self.palette = palette