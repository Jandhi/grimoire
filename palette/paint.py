from data.asset import Asset

BLOCK    = 'block'
SLAB     = 'slab'
STAIRS   = 'stairs'
FENCE    = 'fence'
GATE     = 'gate'
WALL     = 'wall'
TRAPDOOR = 'trapdoor'

class Paint(Asset):
    data : dict[str, str]