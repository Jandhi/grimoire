from gdpc import WorldSlice

def get_biome_map(world_slice : WorldSlice):
    size = world_slice.rect.size
    
    biome_map = [[False for _ in range(size.y)] for _ in range(size.x)]

    for x in range(size.x):
        for z in range(size.y):
            y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z]
            biome = world_slice.getBiome((x, y, z))

            biome_map[x][z] = biome

    return biome_map