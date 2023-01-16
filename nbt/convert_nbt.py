from nbt import nbt

# Converts an nbt file into a more legible python dictionary
# TODO Entities cannot be read in yet
def convert_nbt(filename):
    file = nbt.NBTFile(filename)
    blocks = {}

    for block in file['blocks']:
        x, y, z = (int(i.valuestr()) for i in block['pos'])
        state = block['state']
        
        blocks[(x, y, z)] = int(state.valuestr())

    print(blocks)

    palette = []

    for item in file['palette']:
        block = {}

        if 'Name' in item: 
            block['name'] = item['Name']

        if 'Properties' in item:
            properties = {}

            for property in item['Properties']:
                pname = str(property)
                properties[pname] = str(item['Properties'][pname])

            block['properties'] = properties
                
        palette.append(block)
    
    return {
        'blocks'  : blocks,
        'palette' : palette
    }