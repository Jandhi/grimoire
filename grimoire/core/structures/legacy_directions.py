from gdpc.vector_tools import ivec2, ivec3

LegacyDirection = str

# By Axis
X_PLUS = "x_plus"
X_MINUS = "x_minus"
Y_PLUS = "y_plus"
Y_MINUS = "y_minus"
Z_PLUS = "z_plus"
Z_MINUS = "z_minus"

# By Name
NORTH = Z_MINUS
EAST = X_PLUS
SOUTH = Z_PLUS
WEST = X_MINUS
UP = Y_PLUS
DOWN = Y_MINUS
CARDINAL = (NORTH, EAST, SOUTH, WEST)

# Compound Directions
NORTHEAST = f"{NORTH} and {EAST}"
NORTHWEST = f"{NORTH} and {WEST}"
SOUTHWEST = f"{SOUTH} and {WEST}"
SOUTHEAST = f"{SOUTH} and {EAST}"
ALL_8 = (NORTH, EAST, SOUTH, WEST, NORTHEAST, NORTHWEST, SOUTHWEST, SOUTHEAST)

DIRECTIONS = (NORTH, EAST, SOUTH, WEST, UP, DOWN)

OPPOSITES = {
    X_PLUS: X_MINUS,
    X_MINUS: X_PLUS,
    Y_PLUS: Y_MINUS,
    Y_MINUS: Y_PLUS,
    Z_PLUS: Z_MINUS,
    Z_MINUS: Z_PLUS,
}


def opposite(direction):
    return OPPOSITES[direction]


VECTORS = {
    X_PLUS: ivec3(1, 0, 0),
    X_MINUS: ivec3(-1, 0, 0),
    Y_PLUS: ivec3(0, 1, 0),
    Y_MINUS: ivec3(0, -1, 0),
    Z_PLUS: ivec3(0, 0, 1),
    Z_MINUS: ivec3(0, 0, -1),
}

for dir1, dir2, compound in (
    (NORTH, EAST, NORTHEAST),
    (NORTH, WEST, NORTHWEST),
    (SOUTH, WEST, SOUTHWEST),
    (SOUTH, EAST, SOUTHEAST),
):
    VECTORS[compound] = VECTORS[dir1] + VECTORS[dir2]


def vector(direction: LegacyDirection) -> ivec3:
    return VECTORS[direction]


def get_ivec2(direction: LegacyDirection) -> ivec2:
    tup = vector(direction)
    return ivec2(tup[0], tup[2])


DIRECTIONS_TEXT = {
    NORTH: "north",
    EAST: "east",
    SOUTH: "south",
    WEST: "west",
    UP: "up",
    DOWN: "down",
}


def to_text(direction):
    return DIRECTIONS_TEXT[direction]


TEXT_2_DIRECTION = {
    "north": NORTH,
    "east": EAST,
    "south": SOUTH,
    "west": WEST,
    "up": UP,
    "down": DOWN,
}


def from_text(text: str):
    return TEXT_2_DIRECTION[text]


FORWARDS = {NORTH: NORTH, EAST: EAST, SOUTH: SOUTH, WEST: WEST}
RIGHT = {
    NORTH: EAST,
    EAST: SOUTH,
    SOUTH: WEST,
    WEST: NORTH,
    UP: UP,
    DOWN: DOWN
}
LEFT = {
    NORTH: WEST,
    WEST: SOUTH,
    SOUTH: EAST,
    EAST: NORTH,
    UP: UP,
    DOWN: DOWN
}

BACKWARDS = OPPOSITES

from_ivec2_dict = {
    ivec2(0, -1): NORTH,
    ivec2(0, 1): SOUTH,
    ivec2(1, 0): EAST,
    ivec2(-1, 0): WEST,
}


def ivec2_to_dir(iv2: ivec2):
    return from_ivec2_dict[iv2]


from_ivec3_dict = {
    ivec3(0, 0, -1): NORTH,
    ivec3(0, 0, 1): SOUTH,
    ivec3(1, 0, 0): EAST,
    ivec3(-1, 0, 0): WEST,
}


def ivec3_to_dir(iv3: ivec3):
    return from_ivec3_dict[iv3]


x_mirror = {
    X_PLUS: X_MINUS,
    X_MINUS: X_PLUS,
    Z_PLUS: Z_PLUS,
    Z_MINUS: Z_MINUS,
}

z_mirror = {
    X_PLUS: X_PLUS,
    X_MINUS: X_MINUS,
    Z_PLUS: Z_MINUS,
    Z_MINUS: Z_PLUS,
}

x_z_flip = {
    X_PLUS: Z_PLUS,
    X_MINUS: Z_MINUS,
    Z_PLUS: X_PLUS,
    Z_MINUS: X_MINUS,
}
