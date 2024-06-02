from enum import Enum, auto

from gdpc import Block


class BlockForm(Enum):
    BLOCK = auto()
    STAIRS = auto()
    SLAB = auto()
    WALL = auto()
    FENCE = auto()
    DOOR = auto()
    TRAPDOOR = auto()
    SIGN = auto()

    @staticmethod
    def get_form(block: Block) -> "BlockForm":
        for form in BlockForm:
            if form.name.lower() in block.id:
                return form

        # We assume otherwise it is a whole block
        # This may not necessarily be the case, but it's a *good enough* metric
        return BlockForm.BLOCK
