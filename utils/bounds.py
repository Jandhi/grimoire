from gdpc import WorldSlice
from gdpc.vector_tools import ivec3

def is_in_bounds(point : ivec3, world_slice : WorldSlice) -> bool:
    return point.x >= 0 and point.z >= 0 and point.x < world_slice.box.size.x and point.z < world_slice.box.size.z