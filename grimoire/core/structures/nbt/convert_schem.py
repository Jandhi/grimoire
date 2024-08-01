import sys

from nbtlib import nbt, serialize_tag
from ..structure import Structure
from gdpc.block import Block
from gdpc.vector_tools import ivec3
from itertools import product


# Converts a .schem file into a more legible Structure object
def convert_schem(filename: str) -> Structure:
    file = nbt.load(sys.path[0] + "/" + filename)
    schematic = file["Schematic"]

    width = int(schematic["Width"])
    height = int(schematic["Height"])
    length = int(schematic["Length"])

    offset = ivec3(*list(int(x) for x in schematic["Offset"]))

    blocks = schematic["Blocks"]
    data = blocks["Data"]

    palette = [Block(block_id) for block_id in blocks["Palette"].keys()]

    my_blocks = {}

    for (x, y, z) in product(range(width), range(height), range(length)):
        my_blocks[ivec3(x, y, z) + offset] = (
            data[x + z * width + y * width * length],
            "",
        )
                

    return Structure(my_blocks, {}, palette, ivec3(width, height, length))
