from nbt import nbt
from structures.structure import Structure
from structures.block import Block
from gdpc.vector_tools import ivec3

# Converts an nbt file into a more legible Structure object
# TODO Entities cannot be read in yet
def convert_nbt(filename : str) -> Structure:
    file = nbt.NBTFile(filename)
    blocks, dimensions = __read_blocks_and_dimensions(file['blocks'])
    palette = []

    __read_entities(file['entities'])

    for tag in file['palette']:
        name = ''
        properties = {}

        if 'Name' in tag: 
            name = str(tag['Name'])

        if 'Properties' in tag:
            properties = __read_properties(tag)
                
        palette.append(
            Block(name, properties)
        )
    
    return Structure(blocks, palette, dimensions)

def __read_entities(tag):
    for entity in tag:
        print(entity)

        nbt = entity['nbt']

        print(nbt)


def __read_blocks_and_dimensions(tag) -> dict:
    blocks = {}
    minimums = [0, 0, 0]
    maximums = [0, 0, 0]

    for block in tag:
        x, y, z = (int(i.valuestr()) for i in block['pos'])
        state = block['state']
        
        blocks[ivec3(x, y, z)] = int(state.valuestr())

        for val, index in ((x, 0), (y, 1), (z, 2)):
            if val < minimums[index]:
                minimums[index] = val
            if val > maximums[index]:
                maximums[index] = val

    dimensions = ivec3(*(maximums[i] - minimums[i] for i in range(3)))

    return blocks, dimensions

def __read_properties(tag) -> dict:
    properties = {}

    for property in tag['Properties']:
        pname = str(property)
        properties[pname] = str(tag['Properties'][pname])

    return properties