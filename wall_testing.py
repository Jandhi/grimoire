# Allows code to be run in root directory
import sys
from noise.rng import RNG
from noise.random import randrange
sys.path[0] = sys.path[0].removesuffix('\\structures\\tests')

# Actual file
from structures.directions import north, east, west, south, tuple_dir, directions, left, right, to_text
from utils.tuples import add_tuples, multiply_tuple
from gdpc.interface import requestPlayerArea, Interface
from structures.build_nbt import build_nbt
from structures.nbt_asset import NBTAsset
from structures.transformation import Transformation

def detect_wall(current: tuple[int, int, int], interface)-> list[tuple[int, int, int]]:
    point_list = [current]
    prev = current
    next = find_next_block(current, prev, interface)
    while (next != current):
        point_list.append(next)
        prev = current
        current = next
        next = find_next_block(current, prev, interface)
        print(next)
    return point_list

def build_wall_palisade(wall_points: list[tuple[int, int, int]], interface, rng):
    new_wall_points = []
    #enhancing the wall_points list by adding height
    height = randrange(rng.value(), 4, 7)
    for point in wall_points:
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
            interface.placeBlock(point[0],y,point[2], 'minecraft:oak_log')
        interface.placeBlock(point[0],point[1] + point[3], point[2], 'minecraft:oak_fence')

def find_next_block(current: tuple[int, int, int], previous: tuple[int, int, int], interface, height = 2)-> tuple[int, int, int]:
    for h in range(height * -1, height + 1):
        for check in [[0,h,1],[0,h,-1],[1,h,1],[1,h,-1],[-1,h,1],[-1,h,-1],[-1,h,0],[1,h,0]]:

            next = [current[0]+check[0],current[1]+check[1],current[2]+check[2]]
            #print(next)
            if next != previous:
                if interface.getBlock(next[0], next[1], next[2]) == 'minecraft:red_wool':
                    #print('found')
                    return next
    print(current)
    return current

# given list of wall points and a way to find which is inside (current blue wool)
def enhance_wall_points(wall_points: list[tuple[int, int, int]]):
    enhanced_wall_points = []
    for point in wall_points:
        enhanced_point = [point, [], None]
        for height in (-1, 0, 1):
            for dir in (north, east, west, south):
                check_pt = add_tuples(point, tuple_dir(dir))
                if interface.getBlock(check_pt[0], check_pt[1] + height, check_pt[2]) == 'minecraft:blue_wool':
                    enhanced_point[1].append(dir)
                    #print(dir)
        enhanced_wall_points.append(enhanced_point)

    print(enhanced_wall_points)
    #second pass to remove multi dirs aswells as adding special cases
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

def build_wall_2(wall_points: list[tuple[int, int, int], list[directions], str], interface, rng):
    previous_dir = wall_points[1][1][0]
    for i,wall_point in enumerate(wall_points):
        point = wall_point[0]
        
        if wall_point[2] == 'long_corner':
            dirs = wall_point[1]
            for place_point in [point, add_tuples(point, tuple_dir(dirs[0])), add_tuples(point, tuple_dir(dirs[1])), add_tuples(point, tuple_dir(dirs[0]), tuple_dir(dirs[1])), add_tuples(point, multiply_tuple(tuple_dir(dirs[0]), 2)), add_tuples(point, multiply_tuple(tuple_dir(dirs[1]), 2))]:
                interface.placeBlock(place_point[0],place_point[1] + 8,place_point[2], 'minecraft:oak_slab')
        elif wall_point[2] == 'short_corner':
            interface.placeBlock(point[0],point[1] + 8,point[2], 'minecraft:oak_slab')
        else:
            for y in range(point[1], point[1] + 9):
                interface.placeBlock(point[0],y,point[2], 'minecraft:stone_bricks')
            if len(wall_point[1]) != 0:
                previous_dir = wall_point[1][0]
            interface.placeBlock(point[0],point[1] + 9, point[2], f'minecraft:stone_brick_stairs[facing={to_text(right[previous_dir])}]')
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
                    interface.placeBlock(new_pt[0],new_pt[1] + 8+ height_modifier,new_pt[2], block)
                #inner wall test
                new_pt = add_tuples(point, multiply_tuple(tuple_dir(dir), 5))
                for y in range(new_pt[1], new_pt[1] + 9):
                    interface.placeBlock(new_pt[0],y,new_pt[2], 'minecraft:stone_bricks')
                interface.placeBlock(new_pt[0],new_pt[1] + 9, new_pt[2], f'minecraft:stone_brick_stairs[facing={to_text(right[previous_dir])}]')

area = requestPlayerArea()

print(area)

x_mid = (area[3] + area[0]) // 2 + 1 # player x
z_mid = (area[5] + area[2]) // 2 + 1 # player z

interface = Interface(x_mid,67, z_mid, buffering=True, caching=True)

print(x_mid," 4 ",z_mid)

rng = RNG(0)

points=detect_wall([0,0,0], interface)
#build_wall_palisade(points, interface, rng)
new_pts = enhance_wall_points(points)
build_wall_2(new_pts, interface, rng)
interface.sendBlocks()


#idea, have a util function which given a block, loc, and top / bottom with place two slabs to simulate being a block or block