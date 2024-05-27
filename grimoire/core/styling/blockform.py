from enum import Enum

from gdpc import Block


class BlockForm(Enum):
    block = "block"
    stairs = "stairs"
    slab = "slab"
    wall = "wall"
    fence = "fence"
    door = "door"
    trapdoor = "trapdoor"
    sign = "sign"

    @staticmethod
    def get_form(block: Block) -> "BlockForm":
        for form in BlockForm:
            if form.value in block.id:
                return form

        # We assume otherwise it is a whole block
        # This may not necessarily be the case, but it's a *good enough* metric
        return BlockForm.block
