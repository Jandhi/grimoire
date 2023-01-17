from building.convert_nbt import convert_nbt
from gdpc.interface import Interface

def build_nbt(interface : Interface, filename : str):
    structure = convert_nbt(filename)

    for (pos, palette_index) in structure.blocks.items():
        x, y, z = pos
        block = structure.palette[palette_index]
        interface.placeBlock(x, y, z, str(block)) 