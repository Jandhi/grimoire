from gdpc.vector_tools import ivec3, ivec2
from gdpc import WorldSlice
from glm import normalize, vec2


def x_ivec3(x: int) -> ivec3:
    return ivec3(x, 0, 0)


def y_ivec3(y: int) -> ivec3:
    return ivec3(0, y, 0)


def z_ivec3(z: int) -> ivec3:
    return ivec3(0, 0, z)


def point_3d(point: ivec2, world_slice: WorldSlice) -> ivec3:
    return ivec3(
        point.x,
        world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][point.x][point.y],
        point.y,
    )


def normalize_to_length(vec: ivec2, desired_length: int) -> ivec2:
    normalized_vec = normalize(
        vec2(vec)
    )  # Convert to vec2 for floating point precision
    scaled_vec = normalized_vec * desired_length
    return ivec2(scaled_vec)  # Convert back to ivec2


def mod_xz(point: ivec3, base: int) -> ivec3:
    return ivec3(point.x - point.x % base, point.y, point.z - point.z % base)
