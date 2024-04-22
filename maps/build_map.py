from gdpc import WorldSlice, Block


def get_build_map(world_slice: WorldSlice):
    size = world_slice.rect.size

    # added size buffer
    return [[False for _ in range(size.y + 20)] for _ in range(size.x + 20)]
