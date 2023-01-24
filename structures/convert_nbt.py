from nbt import nbt
from structures.structure import Structure
from structures.block import Block

# Converts an nbt file into a more legible python dictionary
# TODO Entities cannot be read in yet
def convert_nbt(filename : str) -> Structure:
    file = nbt.NBTFile(filename)
    blocks = {}

    for block in file['blocks']:
        x, y, z = (int(i.valuestr()) for i in block['pos'])
        state = block['state']
        
        blocks[(x, y, z)] = int(state.valuestr())

    palette = []

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
    
    return Structure(blocks, palette)

def __read_properties(tag) -> dict:
    properties = {}

    for property in tag['Properties']:
        pname = str(property)
        properties[pname] = str(tag['Properties'][pname])

    return properties