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

cardinal = (north, east , south, west)
opposites = {
    x_plus : x_minus,
    x_minus : x_plus,
    y_plus : y_minus,
    y_minus : y_plus,
    z_plus : z_minus,
    z_minus : z_plus
}

def opposite(direction):
    opposites[direction]

vectors = {
    x_plus  : (1, 0, 0),
    x_minus : (-1, 0, 0),
    y_plus  : (0, 1, 0),
    y_minus : (0, -1, 0),
    z_plus  : (0, 0, 1),
    z_minus : (0, 0, -1)
}
def vector(direction):
    vectors[direction]

text = {
    north : 'north',
    east  : 'east',
    south : 'south',
    west  : 'west',
    up    : 'up',
    down  : 'down',
}
def to_text(direction):
    text[direction]

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