from gdpc.vector_tools import ivec3

def x_vec(x : int) -> ivec3:
    return ivec3(x, 0, 0)

def y_vec(y : int) -> ivec3:
    return ivec3(0, y, 0)

def z_vec(z : int) -> ivec3:
    return ivec3(0, 0, z)