from enum import Enum

from gdpc import Block


class BlockForm(Enum):
    BLOCK = "block"
    STAIRS = "stairs"
    SLAB = "slab"
    WALL = "wall"
    FENCE = "fence"
    DOOR = "door"
    TRAPDOOR = "trapdoor"
    SIGN = "sign"

    @staticmethod
    def get_form(block: Block) -> "BlockForm":
        for form in BlockForm:
            if form.value in block.id:
                return form

        # We assume otherwise it is a whole block
        # This may not necessarily be the case, but it's a *good enough* metric
        return BlockForm.BLOCK
