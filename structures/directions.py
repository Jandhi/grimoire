from structures.types import vec3
from gdpc.vector_tools import ivec2, ivec3

direction = str

# By Axis
x_plus  = 'x_plus'
x_minus = 'x_minus'
y_plus  = 'y_plus'
y_minus = 'y_minus'
z_plus  = 'z_plus'
z_minus = 'z_minus'

# By Name
north = z_minus
east = x_plus
south = z_plus
west = x_minus
up = y_plus
down = y_minus
cardinal = (north, east, south, west)

directions = (north, east, south, west, up, down)

opposites = {
    x_plus : x_minus,
    x_minus : x_plus,
    y_plus : y_minus,
    y_minus : y_plus,
    z_plus : z_minus,
    z_minus : z_plus
}
def opposite(direction):
    return opposites[direction]

vectors = {
    x_plus  : (1, 0, 0),
    x_minus : (-1, 0, 0),
    y_plus  : (0, 1, 0),
    y_minus : (0, -1, 0),
    z_plus  : (0, 0, 1),
    z_minus : (0, 0, -1)
}
def vector(direction : direction) -> vec3:
    return vectors[direction]
def get_ivec2(direction : direction) -> ivec2:
    tup = vector(direction)
    return ivec2(tup[0], tup[2])
def get_ivec3(direction : direction) -> ivec3:
    return ivec3(*vector(direction))

tuples = {
    x_plus  : [1, 0, 0],
    x_minus : [-1, 0, 0],
    y_plus  : [0, 1, 0],
    y_minus : [0, -1, 0],
    z_plus  : [0, 0, 1],
    z_minus : [0, 0, -1]
}
def tuple_dir(direction):
    return tuples[direction]

text_dict = {
    north : 'north',
    east  : 'east',
    south : 'south',
    west  : 'west',
    up    : 'up',
    down  : 'down',
}
def to_text(direction):
    return text_dict[direction]

from_text_dict = {
    'north' : north,
    'east'  : east,
    'south' : south,
    'west'  : west,
    'up'    : up,
    'down'  : down,
}
def from_text(text : str):
    return from_text_dict[text]

forwards = {
    north : north,
    east : east,
    south : south,
    west: west
}
right = {
    north: east,
    east: south,
    south: west,
    west: north,
}
left = {
    north: west,
    west: south,
    south: east,
    east: north
}

backwards = opposites