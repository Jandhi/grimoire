from nbt import nbt

nbtfile = nbt.NBTFile('./schematics/japanese/japanese_wall.nbt')

width, height, depth = nbtfile['size']

for block_tag in nbtfile['blocks']:
    x, y, z = block_tag['pos']
    print(block_tag['state'])
    print(x, y, z)

print(nbtfile)

for tag in nbtfile['palette']:
    print(tag)
    