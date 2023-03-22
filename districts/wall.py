from noise.rng import RNG
from noise.random import randrange
from gdpc import Editor, Block
from gdpc.vector_tools import Rect, ivec2, distance, ivec3
from gdpc import WorldSlice
from structures.directions import north, east, west, south, tuple_dir, directions, left, right, to_text
from utils.tuples import add_tuples, multiply_tuple
from utils.geometry import get_neighbours_in_set

def find_wall_neighbour(current, previous, previous_previous, wall_dict):
    for check in [ivec2(-1,0),ivec2(0,-1),ivec2(1,0),ivec2(0,1),ivec2(-1,-1),ivec2(-1,1),ivec2(1,-1),ivec2(1,1)]:
        next_wall_point = current + check
        if next_wall_point != previous and next_wall_point != previous_previous and wall_dict.get(next_wall_point) == True:
            return next_wall_point

#orders the list of wall points based off the first point in the list
def order_wall_points(wall_points: list[ivec2], wall_dict: dict) -> list[ivec2]:
    ordered_wall_points: list[ivec2] = []

    ordered_wall_points.append(wall_points[0])
    current_wall_point = ordered_wall_points[0]
    previous_point = ordered_wall_points[0]
    previous_previous_point = ordered_wall_points[0]
    while len(ordered_wall_points) != len(wall_points):
        next_wall_point = find_wall_neighbour(current_wall_point, previous_point, previous_previous_point, wall_dict)
        ordered_wall_points.append(next_wall_point)
        previous_previous_point = previous_point
        previous_point = current_wall_point
        current_wall_point = next_wall_point

    return ordered_wall_points

def build_wall(wall_points: list[ivec2], wall_dict: dict, editor : Editor, world_slice : WorldSlice, rng : RNG, wall_type : str):
    if wall_type == 'palisade':
        build_wall_palisade(wall_points, editor, world_slice, rng)
    elif wall_type == 'standard':
        build_wall_standard(wall_points, wall_dict, editor, world_slice, rng)

def build_wall_palisade(wall_points: list[ivec2], editor : Editor, world_slice : WorldSlice, rng):
    new_wall_points = []
    height_map = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']
    #enhancing the wall_points list by adding height
    height = randrange(rng.value(), 4, 7)
    for vec in wall_points:
        point = [vec.x,height_map[vec.x][vec.y],vec.y]
        point+=[height]
        new_wall_points.append(point)
        # ensuring next wall piece is a different height
        next_height = randrange(rng.value(), 4, 7)
        while (height == next_height):
            next_height = randrange(rng.value(), 4, 7)
        height = next_height

    #sorting by height, so lowest sections get built first
    new_wall_points.sort(key = lambda a: a[3])

    for point in new_wall_points:
        for y in range(point[1], point[1] + point[3]):
            #interface.placeBlock(point[0],y,point[2], 'minecraft:stone_bricks')
        #interface.placeBlock(point[0],point[1] + point[3], point[2], 'minecraft:stone_brick_wall')
            editor.placeBlock((point[0],y,point[2]), Block('minecraft:oak_log'))
        editor.placeBlock((point[0],point[1] + point[3], point[2]), Block('minecraft:oak_fence'))


def build_wall_standard(wall_points: list[ivec2], wall_dict : dict, editor : Editor, world_slice : WorldSlice, rng):

    wall_points = add_wall_points_directionality(wall_points, wall_dict)

    #need to fix heights likley here
    new_wall_points = []
    height_map = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']
    #enhancing the wall_points list by adding height
    height = randrange(rng.value(), 4, 7)
    for vec in wall_points:
        point = [vec.x,height_map[vec.x][vec.y],vec.y]
        point+=[height]
        new_wall_points.append(point)
        # ensuring next wall piece is a different height
        next_height = randrange(rng.value(), 4, 7)
        while (height == next_height):
            next_height = randrange(rng.value(), 4, 7)
        height = next_height

    previous_dir = wall_points[1][1][0]
    for i,wall_point in enumerate(wall_points):
        point = wall_point[0]
        
        if wall_point[2] == 'long_corner':
            dirs = wall_point[1]
            for place_point in [point, add_tuples(point, tuple_dir(dirs[0])), add_tuples(point, tuple_dir(dirs[1])), add_tuples(point, tuple_dir(dirs[0]), tuple_dir(dirs[1])), add_tuples(point, multiply_tuple(tuple_dir(dirs[0]), 2)), add_tuples(point, multiply_tuple(tuple_dir(dirs[1]), 2))]:
                editor.placeBlock(place_point[0],place_point[1] + 8,place_point[2], 'minecraft:oak_slab')
        elif wall_point[2] == 'short_corner':
            editor.placeBlock(point[0],point[1] + 8,point[2], 'minecraft:oak_slab')
        else:
            for y in range(point[1], point[1] + 9):
                editor.placeBlock(point[0],y,point[2], 'minecraft:stone_bricks')
            if len(wall_point[1]) != 0:
                previous_dir = wall_point[1][0]
            editor.placeBlock(point[0],point[1] + 9, point[2], f'minecraft:stone_brick_stairs[facing={to_text(right[previous_dir])}]')
            for dir in wall_point[1]:
                block = 'minecraft:oak_slab'
                height_modifier = 0 #used in one case to alter height of walkway
                if i == 0 or i == len(wall_points) - 1:
                    if i == 0 and wall_points[i+1][0][1] == point[1] + 1:
                        block = 'minecraft:oak_slab[type=top]'
                    elif i == len(wall_points) - 1 and wall_points[i-1][0][1] == point[1] + 1:
                        block = 'minecraft:oak_slab[type=top]'
                    else:
                        block = 'minecraft:oak_slab'
                else: #making a nice path along the walls
                    prev_h = wall_points[i-1][0][1]
                    next_h = wall_points[i+1][0][1]
                    h = point[1]
                    if (prev_h == h and next_h == h + 1) or (prev_h == h + 1 and next_h == h):
                        block = 'minecraft:oak_slab[type=top]'
                    elif (prev_h == h and next_h == h - 1) or (prev_h == h - 1 and next_h == h):
                        block = 'minecraft:oak_slab'
                    elif prev_h == h - 1 and next_h == h + 1:
                        block = f'minecraft:oak_stairs[facing={to_text(right[dir])}]'
                    elif prev_h == h + 1 and next_h == h - 1:
                        block = f'minecraft:oak_stairs[facing={to_text(left[dir])}]' 
                    elif prev_h == h + 1 and next_h == h + 1:
                        block = 'minecraft:oak_slab[type=top]'
                    elif prev_h == h - 1 and next_h == h - 1:
                        block = 'minecraft:oak_slab[type=top]'
                        height_modifier = -1
                for x in range(1, 5):
                    new_pt = add_tuples(point, multiply_tuple(tuple_dir(dir), x))
                    editor.placeBlock(new_pt[0],new_pt[1] + 8+ height_modifier,new_pt[2], block)
                #inner wall test
                new_pt = add_tuples(point, multiply_tuple(tuple_dir(dir), 5))
                for y in range(new_pt[1], new_pt[1] + 9):
                    editor.placeBlock(new_pt[0],y,new_pt[2], 'minecraft:stone_bricks')
                editor.placeBlock(new_pt[0],new_pt[1] + 9, new_pt[2], f'minecraft:stone_brick_stairs[facing={to_text(right[previous_dir])}]')

def add_wall_points_directionality(wall_points, wall_dict):
    enhanced_wall_points = []
    for point in wall_points:
        enhanced_point = [point, [], None]
        neighbours = get_neighbours_in_set(point, wall_points)
        for neighbour in neighbours:
            if wall_dict.get(neighbour) != True:
                enhanced_point[1].append(neighbour - point) #might need to change for vec3, since I dont care about height here

        enhanced_wall_points.append(enhanced_point)

    print(enhanced_wall_points)
    #second pass to remove multi dirs as wells as adding special cases
    special_points = []
    for i,point in enumerate(enhanced_wall_points):
        if len(point[1]) > 1:
            remove_dirs = [] 
            for dir in point[1]:
                if dir in enhanced_wall_points[i-1][1] and i != 0:
                    continue
                elif i != len(enhanced_wall_points)-1 and left[dir] in enhanced_wall_points[i+1][1] and len(enhanced_wall_points[i+1][1])>1:
                    remove_dirs.append(dir)
                    if len(enhanced_wall_points[i+1][1]) > 1:
                        enhanced_wall_points[i+1][1].remove(left[dir])
                        special_points.append([add_tuples(point[0], tuple_dir(dir)), [dir, left[dir]], 'long_corner'])
                elif i != len(enhanced_wall_points)-1 and right[dir] in enhanced_wall_points[i+1][1] and len(enhanced_wall_points[i+1][1])>1:
                    remove_dirs.append(dir)
                    if len(enhanced_wall_points[i+1][1]) > 1:
                        enhanced_wall_points[i+1][1].remove(right[dir])
                        special_points.append([add_tuples(point[0], tuple_dir(dir)), [dir, right[dir]], 'long_corner'])
                elif (left[dir] in enhanced_wall_points[i-1][1] or right[dir] in enhanced_wall_points[i-1][1]) and i != 0:
                    remove_dirs.append(dir)
            for dir in remove_dirs: # remove dirs from the list after they all have been checked
                enhanced_wall_points[i][1].remove(dir)
        elif len(point[1]) == 1:
            dir = point[1][0]
            if i != len(enhanced_wall_points)-1 and left[dir] in enhanced_wall_points[i+1][1]:
                if len(enhanced_wall_points[i+1][1]) == 1: #only short corner if both are of size 1
                    enhanced_wall_points[i][1].remove(dir)
                    special_points.append([add_tuples(point[0], tuple_dir(dir)), [dir, left[dir]], 'short_corner'])
                enhanced_wall_points[i+1][1].remove(left[dir])
            elif i != len(enhanced_wall_points)-1 and right[dir] in enhanced_wall_points[i+1][1] and  len(enhanced_wall_points[i+1][1]) == 1:
                if len(enhanced_wall_points[i+1][1]) == 1: #only short corner if both are of size 1
                    enhanced_wall_points[i][1].remove(dir)
                    special_points.append([add_tuples(point[0], tuple_dir(dir)), [dir, right[dir]], 'short_corner'])
                enhanced_wall_points[i+1][1].remove(right[dir])
                

            
    enhanced_wall_points.extend(special_points)
    print(enhanced_wall_points)

    return enhanced_wall_points