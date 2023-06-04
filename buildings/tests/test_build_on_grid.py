# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\buildings\\tests')

import numpy as np

SEED = 1293786

# Actual file
from gdpc.editor import Editor
from structures.grid import Grid
from buildings.walls.wall import Wall
#from buildings.roofs.roof import Roof
from buildings.rooms.room import Room


from data.load_assets import load_assets
from structures.directions import cardinal, get_ivec3, opposite, right, up, north, east, south, west

from style.style import Style
from palette.palette import Palette

editor = Editor(buffering=True, caching=True)

from noise.rng import RNG

from gdpc.vector_tools import ivec3

area = editor.getBuildArea()
editor.transform = (area.begin.x, 3, area.begin.z)
grid = Grid()
load_assets('assets')

rng = RNG(SEED, 'get_origins')

styles = {
    'japanese' : {
        'lower' : 'japanese_wall_bottom_plain',
        'upper'  : 'japanese_wall_upper_traps',
        'roof'   : 'japanese_roof_flat_brick_single'
    },
    'viking' : {
        'lower'  : 'viking_wall_lower_stone_base_window',
        'upper'  : 'viking_wall_upper_logs_window',
        'roof'   : 'viking_roof_stone_accent_single'
    }
}
style = styles['viking']

# PALETTE
palette : Palette = Palette.find('japanese_dark_blackstone')

# WALLS
lower_wall : Wall = Wall.find(style['lower'])
upper_wall : Wall = Wall.find(style['upper'])

ROOM_LIST = [
     'kitchen_no_window_small',
     'kitchen_corner_1',
     'bedroom1',
     'bedroom_centered',
     'bedroom_corner',
     'hallway_1'
]

CONNECTION_LIST = [
    'wall',
    'open'
]

LOWER_STAIRCASE_LIST = [
    'staircase_corner_lower'
]

UPPER_STAIRCASE_LIST = [
    'staircase_corner_upper'
]

ONEBYONE_UPPER_LIST = [
    '1x1_twostorey_upper_1'
]

ONEBYONE_LOWER_LIST = [
    '1x1_twostorey_lower_1'
]

ONEBYONE_LIST = [
    '1x1_room_1'
]


def rotate(a: list,n=1) -> list:
    if len(a) == 0:
        return a
    n = -n % len(a)     # flip rotation direction
    return np.concatenate((a[n:],a[:n]))  

def is_corner(cell_to_check: ivec3, cells_to_fill: list) -> tuple:
    corner_combinations = [
        ["wall", "wall", "open", "open"],
        ["open", "wall", "wall", "open"],
        ["open", "open", "wall", "wall"],
        ["wall", "open", "open", "wall"]
    ]

    test = []
    for direction in cardinal:
        neighbor = cell_to_check + get_ivec3(direction)
        if neighbor in cells_to_fill:
            test.append('open')
        else:
            test.append('wall')
    
    return test in corner_combinations, test


def build_start(cells_with_rooms: list, cells_to_fill: list) -> list:
    start_connections = []
    start = rng.choose(cells_to_fill)
    for direction in cardinal:
        neighbor = start + get_ivec3(direction)
        if neighbor in cells_to_fill:
            start_connections.append('open')
        else:
            start_connections.append('wall')

    #find a room in that fits in that spot
    potential_rooms = []
    for room_name in ROOM_LIST:
        room : Room = Room.find(room_name)
        to_face = room.facing
        for i in range(4):
            if list(rotate(room.connections, i)) == start_connections:
                potential_rooms.append((room, to_face, rotate(room.connections, i)))

            if i > 0:
                to_face = right[to_face]

    room_to_build, room_facing, connections = rng.choose(potential_rooms)
    cells_with_rooms.append((start, connections))
    grid.build(editor, room_to_build, palette, start, facing = room_facing)

    return cells_with_rooms

def build_staircase(level: int, cells_with_rooms: list, cells_to_fill: list) -> list:
    possible_starts = []
    for potential_start in cells_to_fill:
        if is_corner(potential_start, cells_to_fill)[0] and potential_start + get_ivec3(up) in cells_to_fill and potential_start not in cells_with_rooms and list(potential_start)[1] == level:
            possible_starts.append(potential_start)

    start = rng.choose(possible_starts)
    start_connections = is_corner(start, cells_to_fill)[1]

    potential_rooms = []
    for room_name in LOWER_STAIRCASE_LIST:
        room : Room = Room.find(room_name)
        to_face = room.facing
        for i in range(4):
            if list(rotate(room.connections, i)) == start_connections:
                potential_rooms.append((room, to_face, rotate(room.connections, i)))

            if i > 0:
                to_face = right[to_face]

    room_to_build, room_facing, connections = rng.choose(potential_rooms)

    cells_with_rooms.append((start, connections))
    cells_with_rooms.append((start + get_ivec3(up), connections))
    grid.build(editor, room_to_build, palette, start, facing = room_facing)
    room_to_build : Room = Room.find('staircase_corner_upper')
    grid.build(editor, room_to_build, palette, start + get_ivec3(up), facing = room_facing)

    return cells_with_rooms

def get_neighbors(rooms: list, inside_cells: list) -> set:
    neighbors = set()
    for room in rooms:
        for direction in cardinal:
            new_cell = room + get_ivec3(direction)
            if new_cell not in rooms and new_cell in inside_cells:
                neighbors.add(new_cell)
    return neighbors

def populate_floor(level: int, cells_with_rooms: list, cells_to_fill: list) -> list:
    rooms_on_floor = [((x ,y, z), con) for (x, y, z), con in cells_with_rooms if y == level]
    cells_on_floor = [(x, y, z) for x, y, z in cells_to_fill if y == level]
    while len(rooms_on_floor) != len(cells_on_floor):
        candidates = []
        #get the connections for the new rooms
        for neighbor in get_neighbors([x for x, y in rooms_on_floor], cells_on_floor):
            north_con, east_con, south_con, west_con = None, None, None, None
            for c, conns in rooms_on_floor:
                for direction in cardinal:
                    if neighbor + get_ivec3(direction) == c:
                        if direction == north:
                            north_con = conns[2]
                        elif direction == east:
                            east_con = conns[3]
                        elif direction == south:
                            south_con = conns[0]
                        elif direction == west:
                            west_con = conns[1]

            for direction in cardinal:
                if (neighbor + get_ivec3(direction)) not in cells_on_floor:
                    if direction == north:
                        north_con = 'wall'
                    elif direction == east:
                        east_con = 'wall'
                    elif direction == south:
                        south_con = 'wall'
                    elif direction == west:
                        west_con = 'wall'

            new_conns = [north_con, east_con, south_con, west_con]

            #i have definitely found the worst way to do this but I just need it to work for now

            entropy = 0
            potential_rooms = []

            none_idx = []
            for idx, val in enumerate(new_conns):
                if val is None:
                    none_idx.append(idx)
            
            for i0 in CONNECTION_LIST:
                for i1 in CONNECTION_LIST:
                    for i2 in CONNECTION_LIST:
                        for i3 in CONNECTION_LIST:
                            temp = new_conns
                            for ni in none_idx:
                                if ni == 0:
                                    temp[0] = i0
                                elif ni == 1:
                                    temp[1] = i1
                                elif ni == 2:
                                    temp[2] = i2
                                elif ni == 3:
                                    temp[3] = i3

                            for room_name in ROOM_LIST:
                                room: Room = Room.find(room_name)
                                to_face = room.facing
                                for i in range(4):
                                    if list(rotate(room.connections, i)) == temp:
                                        if (room, to_face,  list(rotate(room.connections, i))) not in potential_rooms:
                                            potential_rooms.append((room, to_face, tuple(rotate(room.connections, i))))

                                    if i > 0:
                                        to_face = right[to_face]

            entropy = len(potential_rooms)
            candidates.append((neighbor, entropy, potential_rooms))


        min_entropy = min([y for x, y, z in candidates])
        candidates_with_min_entropy = [(x, y, z) for x, y, z in candidates if y == min_entropy]
        cell_to_build, ent, room_to_build = candidates_with_min_entropy[rng.randint(len(candidates_with_min_entropy))]
        room_to_build, room_facing, connections = rng.choose(room_to_build)

        rooms_on_floor.append((cell_to_build, connections))
        cells_with_rooms.append((cell_to_build, connections))
        grid.build(editor, room_to_build, palette, cell_to_build, facing = room_facing)

    return cells_with_rooms

def build_one_by_one(num_levels: int, cells_to_fill: list) -> None:
    if num_levels == 1:
        cell = cells_to_fill[0]
        pick = rng.choose(ONEBYONE_LIST)
        room_to_build : Room = Room.find(pick)
        grid.build(editor, room_to_build, palette, cell)
    else:
        cell = [(x, y, z) for x, y, z in cells_to_fill if y == 0][0]
        lower_pick = rng.choose(ONEBYONE_LOWER_LIST)
        upper_pick = rng.choose(ONEBYONE_UPPER_LIST)
        
        lower_room : Room = Room.find(lower_pick)
        upper_room : Room = Room.find(upper_pick)

        grid.build(editor, lower_room, palette, cell)
        grid.build(editor, upper_room, palette, cell + get_ivec3(up))



def furnish(cells_to_fill: list) -> None:
    number_of_floors = max([y for (x, y, z) in cells_to_fill]) + 1
    cells_with_rooms = []

    if len(cells_to_fill) == 1 or len(cells_to_fill) == 2 and number_of_floors == 2:
        build_one_by_one(number_of_floors, cells_to_fill)
    else:
        for level in range(number_of_floors):
            if number_of_floors == 1:
                cells_with_rooms = build_start(cells_with_rooms, cells_to_fill)
            elif level != number_of_floors - 1:
                cells_with_rooms = build_staircase(level, cells_with_rooms, cells_to_fill)

            cells_with_rooms = populate_floor(level, cells_with_rooms, cells_to_fill)



