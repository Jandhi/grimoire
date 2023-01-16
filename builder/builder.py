from gdpc.interface import requestPlayerArea, Interface

area = requestPlayerArea()

print(area)

interface = Interface(area[0], area[1], area[2], buffering=True, caching=True)

x_mid = (area[3] - area[0]) // 2 + 1 # player x
z_mid = (area[5] - area[2]) // 2 + 1 # player z

interface.placeBlock(x_mid, 10, z_mid, 'cobblestone')

interface.sendBlocks()