from noise.rng import RNG
from noise.random import randrange
from gdpc import Editor, Block
from gdpc.vector_tools import Rect, ivec2, distance, ivec3
from gdpc import WorldSlice
from structures.directions import north, east, west, south, get_ivec2, directions, left, right, to_text, ivec2_to_dir, get_ivec3, cardinal, opposite
from utils.geometry import get_neighbours_in_set, is_straight_ivec2

def find_wall_neighbour(current, wall_dict, ordered_wall_dict):
    for check in [ivec2(-1,0),ivec2(0,-1),ivec2(-1,-1),ivec2(-1,1),ivec2(1,-1),ivec2(1,0),ivec2(0,1),ivec2(1,1)]: #prefers to go right
        if current == None: #error case
            return None 
        next_wall_point = current + check
        if ordered_wall_dict.get(next_wall_point) != True and wall_dict.get(next_wall_point) == True:
            return next_wall_point

#orders the list of wall points based off the first point in the list
def order_wall_points(wall_points: list[ivec2], wall_dict: dict) -> list[ivec2]:
    ordered_wall_points: list[ivec2] = []
    ordered_wall_dict: dict() = {}
    reverse_checked = False

    ordered_wall_points.append(wall_points[0])
    ordered_wall_dict[wall_points[0]] = True
    current_wall_point = ordered_wall_points[0]
    while len(ordered_wall_points) != len(wall_points):
        next_wall_point = find_wall_neighbour(current_wall_point, wall_dict, ordered_wall_dict)
        if next_wall_point == None: #error case, clean stopping
            if reverse_checked == False: #after the first error, we reverse list and check the other way
                print("reverse")
                reverse_checked = True
                ordered_wall_points.reverse()
                current_wall_point = ordered_wall_points[-1]
            else:
                print('failed')
                break
        else:
            print(next_wall_point)
            ordered_wall_points.append(next_wall_point)
            ordered_wall_dict[next_wall_point] = True
            current_wall_point = next_wall_point

    return ordered_wall_points

def build_wall(wall_points: list[ivec2], wall_dict: dict, editor : Editor, world_slice : WorldSlice, rng : RNG, wall_type : str):
    if wall_type == 'palisade':
        build_wall_palisade(wall_points, editor, world_slice, rng)
    elif wall_type == 'standard':
        build_wall_standard(wall_points, wall_dict, editor, world_slice, rng)

def build_wall_palisade(wall_points: list[ivec2], editor : Editor, world_slice : WorldSlice, water_map, rng):
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
        if water_map[point[0]][point[2]] == False:
            for y in range(point[1], point[1] + point[3]):
                #interface.placeBlock(point[0],y,point[2], 'minecraft:stone_bricks')
            #interface.placeBlock(point[0],point[1] + point[3], point[2], 'minecraft:stone_brick_wall')
                editor.placeBlock((point[0],y,point[2]), Block('minecraft:oak_log'))
            editor.placeBlock((point[0],point[1] + point[3], point[2]), Block('minecraft:oak_fence'))


def build_wall_standard(wall_points: list[ivec2], wall_dict : dict, inner_points: list[ivec2], editor : Editor, world_slice : WorldSlice, water_map):

    wall_points = add_wall_points_height(wall_points, wall_dict, world_slice)
    wall_points = add_wall_points_directionality(wall_points, wall_dict, inner_points)
    height_map = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']

    previous_dir = north

    walkway_list = [] #idea is to get this list and then get the new inner points of hte wall, how do I get height to those
    walkway_dict: dict() = {}

    for i,wall_point in enumerate(wall_points):
        point = wall_point[0]

        for y in range(height_map[point.x, point.z], point.y + 1):
            editor.placeBlock((point.x,y,point.z), Block('minecraft:stone_bricks'))
        if len(wall_point[1]) != 0:
            previous_dir = wall_point[1][0]
        editor.placeBlock((point.x,point.y + 1, point.z), Block(f'minecraft:stone_brick_stairs[facing={to_text(right[previous_dir])}]'))
        for dir in wall_point[1]:
            height_modifier = 0 #used in one case to alter height of walkway
            if i == 0 or i == len(wall_points) - 1:
                continue
            else: 
                prev_h = wall_points[i-1][0].y
                next_h = wall_points[i+1][0].y
                h = point.y
                if prev_h == h - 1 and next_h == h - 1:
                    height_modifier = -1
            if right[dir] in wall_point[1]: # add corner bits for walkway
                for new_pt in (point + get_ivec3(dir) + get_ivec3(right[dir]), point + get_ivec3(dir) + get_ivec3(right[dir]) * 2,point + get_ivec3(dir) *2 + get_ivec3(right[dir])):
                    if wall_dict.get(ivec2(new_pt.x, new_pt.z)) == True:
                        break
                    if walkway_dict.get(ivec2(new_pt.x, new_pt.z)) == None:
                        walkway_list.append(ivec2(new_pt.x, new_pt.z))
                        walkway_dict[ivec2(new_pt.x, new_pt.z)] = new_pt.y + height_modifier
            for x in range(1, 4):
                new_pt = point + get_ivec3(dir) * x
                if wall_dict.get(ivec2(new_pt.x, new_pt.z)) == True:
                    break
                if walkway_dict.get(ivec2(new_pt.x, new_pt.z)) == None:
                    walkway_list.append(ivec2(new_pt.x, new_pt.z))
                    walkway_dict[ivec2(new_pt.x, new_pt.z)] = new_pt.y + height_modifier

    flatten_walkway(walkway_list, walkway_dict, editor)

def build_wall_standard_with_inner(wall_points: list[ivec2], wall_dict : dict, inner_points: list[ivec2], editor : Editor, world_slice : WorldSlice, water_map):

    wall_points = add_wall_points_height(wall_points, wall_dict, world_slice)
    wall_points = add_wall_points_directionality(wall_points, wall_dict, inner_points)
    wall_points = check_water(wall_points, water_map)
    height_map = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']

    previous_dir = north

    walkway_list = [] #idea is to get this list and then get the new inner points of hte wall, how do I get height to those
    walkway_dict: dict() = {}

    inner_wall_list = []

    for i,wall_point in enumerate(wall_points):
        point = wall_point[0]
        if wall_point[2] == 'water':
            continue
        else:
            if wall_point[2] == 'bridge':
                editor.placeBlock((point.x,point.y,point.z), Block('minecraft:stone_bricks'))
            else:
                for y in range(height_map[point.x, point.z], point.y + 1):
                    editor.placeBlock((point.x,y,point.z), Block('minecraft:stone_bricks'))
            if len(wall_point[1]) != 0:
                previous_dir = wall_point[1][0]
            editor.placeBlock((point.x,point.y + 1, point.z), Block(f'minecraft:stone_brick_stairs[facing={to_text(right[previous_dir])}]'))
            for dir in wall_point[1]:
                height_modifier = 0 #used in one case to alter height of walkway
                if i == 0 or i == len(wall_points) - 1:
                    continue
                else: 
                    prev_h = wall_points[i-1][0].y
                    next_h = wall_points[i+1][0].y
                    h = point.y
                    if prev_h == h - 1 and next_h == h - 1:
                        height_modifier = -1
                if right[dir] in wall_point[1]: # add corner bits for walkway
                    for new_pt in (point + get_ivec3(dir) + get_ivec3(right[dir]), point + get_ivec3(dir) + get_ivec3(right[dir]) * 2,point + get_ivec3(dir) *2 + get_ivec3(right[dir])):
                        if wall_dict.get(ivec2(new_pt.x, new_pt.z)) == True:
                            break
                        if walkway_dict.get(ivec2(new_pt.x, new_pt.z)) == None:
                            walkway_list.append(ivec2(new_pt.x, new_pt.z))
                            walkway_dict[ivec2(new_pt.x, new_pt.z)] = new_pt.y + height_modifier
                    #inner wall
                    for wall_pt in (point + get_ivec3(dir)*2 + get_ivec3(right[dir])*2, point + get_ivec3(dir) + get_ivec3(right[dir]) * 3,point + get_ivec3(dir) *3 + get_ivec3(right[dir])):
                        if wall_dict.get(ivec2(wall_pt.x, wall_pt.z)) != True and walkway_dict.get(ivec2(wall_pt.x, wall_pt.z)) == None:
                            inner_wall_list.append(ivec3(wall_pt.x,point.y,wall_pt.z))
                for x in range(1, 4):
                    new_pt = point + get_ivec3(dir) * x
                    if wall_dict.get(ivec2(new_pt.x, new_pt.z)) == True:
                        break
                    if walkway_dict.get(ivec2(new_pt.x, new_pt.z)) == None:
                        walkway_list.append(ivec2(new_pt.x, new_pt.z))
                        walkway_dict[ivec2(new_pt.x, new_pt.z)] = new_pt.y + height_modifier
                        #inner wall
                        if x == 3:
                            wall_pt = point + get_ivec3(dir) * 4
                            if wall_dict.get(ivec2(wall_pt.x, wall_pt.z)) != True and walkway_dict.get(ivec2(wall_pt.x, wall_pt.z)) == None:
                                inner_wall_list.append(ivec3(wall_pt.x,point.y,wall_pt.z))

    for pt in inner_wall_list:
        if water_map[pt.x][pt.z] == True:
            continue
        elif walkway_dict.get(ivec2(pt.x, pt.z)) == None: #check again since walkway was not completed as inner wall was being added
            for y in range(height_map[pt.x, pt.z], pt.y + 1):
                editor.placeBlock((pt.x,y,pt.z), Block('minecraft:stone_bricks'))

    flatten_walkway(walkway_list, walkway_dict, editor)

#adds direction to the wall points to know which way we need to build walkways
def add_wall_points_directionality(wall_points, wall_dict, inner_points):
    enhanced_wall_points = []
    for point in wall_points:  
        enhanced_point = [point, [], None]
        ivec2_point = ivec2(point.x,point.z)
        neighbours = get_neighbours_in_set(ivec2_point, inner_points)
        for neighbour in neighbours:
            if wall_dict.get(neighbour) != True:
                enhanced_point[1].append(ivec2_to_dir(neighbour - ivec2_point))

        enhanced_wall_points.append(enhanced_point)

    return enhanced_wall_points

#this will be complex later
def add_wall_points_height(wall_points, wall_dict, world_slice):
    #print(wall_points)
    height_wall_points = []
    height_map = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']
    current_height = height_map[wall_points[0].x,wall_points[0].y]
    target_height = current_height
    for i,point in enumerate(wall_points):
        if i %5 == 0:
            if len(wall_points)-1 < i+5:
                target_height = height_map[wall_points[len(wall_points)-1].x,wall_points[len(wall_points)-1].y]
            else:
                target_height = height_map[wall_points[i+5].x,wall_points[i+5].y]
        #add a check to see for drastic height difference
        if current_height != target_height and ( 1 < i < len(wall_points)-2):
            if is_straight_ivec2(wall_points[i-2], wall_points[i+2], 4):
                if current_height < target_height:
                    current_height += 1
                elif current_height > target_height:
                    current_height -= 1
        new_point = ivec3(point.x, current_height + 15,point.y) #15 is just a test value for now
        height_wall_points.append(new_point)
    #print(height_wall_points)
    return height_wall_points

RANGE = 3
NEIGHBOURS = [(x, z) for x in range(-RANGE, RANGE + 1) for z in range(-RANGE, RANGE + 1)]

def flatten_walkway(walkway_list, walkway_dict, editor):

    for point in walkway_list:
        walkway_dict[point] = (average_neighbour_height(point.x, point.y, walkway_dict))

    #first pass places slabs and changes dict heights
    for key in walkway_dict:
        height = walkway_dict[key]
        if height % 1 <= 0.25:
            editor.placeBlock((key.x,round(height),key.y), Block('minecraft:oak_slab'))
            walkway_dict[key] = round(height)
        elif 0.25 < height % 1 <= 0.5:
            editor.placeBlock((key.x,round(height),key.y), Block('minecraft:oak_slab[type=top]'))
            walkway_dict[key] = round(height)+0.49
        elif 0.5 < height % 1 <= 0.75:
            editor.placeBlock((key.x,round(height)-1,key.y), Block('minecraft:oak_slab[type=top]'))
            walkway_dict[key] = round(height)-0.51
        else:
            editor.placeBlock((key.x,round(height),key.y), Block('minecraft:oak_slab'))
            walkway_dict[key] = round(height)

    #2nd pass to add stairs based on first pass changes
    for key in walkway_dict:
        height = walkway_dict[key]
        for direction in cardinal:
            delta = get_ivec2(direction)
            neighbour = key + delta
            if walkway_dict.get(neighbour) == None:
                continue
            elif height % 1 ==0: # bottom slab
                if walkway_dict.get(neighbour) - height >= 1:
                    editor.placeBlock((key.x,round(height), key.y), Block(f'minecraft:oak_stairs[facing={to_text(direction)}]'))
            else: #top slab
                if walkway_dict.get(neighbour) - height <= -1:
                    editor.placeBlock((key.x,round(height), key.y), Block(f'minecraft:oak_stairs[facing={to_text(opposite(direction))}]'))


def average_neighbour_height(x : int, z : int, walkway_dict) -> int:
    height_sum = 0
    total_weight = 0

    for dx, dz in NEIGHBOURS:
        if ivec2(x + dx, z + dz) not in walkway_dict: # we only need to flatten for within a district
            continue
        elif abs(walkway_dict[ivec2(x + dx, z + dz)] - walkway_dict[ivec2(x,z)]) >= 4: #ignore extremes
            continue

        distance = abs(dx) + abs(dz)
        weight = 0.8 ** distance
        height = walkway_dict[ivec2(x + dx,z + dz)]
        height_sum += height * weight
        total_weight += weight

    return (height_sum / total_weight)

WATER_CHECK = 20 #the distance to land in either direction the point needs to still be a valid bridge walkway
#water checking
def check_water(wall_points, water_map):
    bridgeable = False #bool, if true, set to bridge, water otherwise
    long_water = True #assume water start
    for i,wall_pt in enumerate(wall_points):
        point = wall_pt[0]

        if water_map[point.x][point.z] == True:
            if long_water:
                wall_points[i][2] = 'water'
            elif bridgeable:
                wall_points[i][2] = 'bridge'

            else: #check if can bridge
                wall_points[i][2] = 'water' #default
                for a in range(1,WATER_CHECK+1):
                    if a+i>=len(wall_points): #OUT OF BOUNDS
                        break
                    pt = wall_points[a+i][0]
                    if water_map[pt.x][pt.z] == False: #found land within range
                        bridgeable = True
                        long_water = False
                        wall_points[i][2] = 'bridge'
                        break
                    elif a == WATER_CHECK:
                        long_water = True
        elif water_map[point.x][point.z] == False:
            bridgeable = False #reset bridgeability
            long_water = False

    return wall_points