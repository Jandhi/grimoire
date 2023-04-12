from gdpc import WorldSlice

Highway = 'highway'
Building = 'building'

def get_initial_building_map(world_slice : WorldSlice):
    size = world_slice.rect.size
    return [[None for _ in range(size.y)] for _ in range(size.x)]