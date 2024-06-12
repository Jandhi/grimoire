# Allows code to be run in root directory
import sys

sys.path[0] = sys.path[0].removesuffix("tests\\buildings")

SEED = 12378623

# Actual file
from gdpc.editor import Editor, Block
from grimoire.core.structures.grid import Grid
from grimoire.buildings.walls.wall import Wall

# from buildings.roofs.roof import Roof
from grimoire.buildings.rooms.room import Room

from grimoire.core.structures.nbt import build_nbt


from grimoire.core.assets.load_assets import load_assets
from grimoire.core.structures.directions import Directions, Direction

from grimoire.palette import Palette
from grimoire.buildings.roofs.roof import Roof

editor = Editor(buffering=True, caching=True)

from grimoire.core.noise.rng import RNG

from gdpc.vector_tools import ivec3

area = editor.getBuildArea()
editor.transform = (area.begin.x, 3, area.begin.z)
grid = Grid()
load_assets("grimoire/asset_data")

rng = RNG(SEED, "get_origins")

styles = {
    "japanese": {
        "lower": "japanese_wall_bottom_plain",
        "upper": "japanese_wall_upper_traps",
        "roof": "japanese_roof_flat_brick_single",
    },
    "viking": {
        "lower": "viking_wall_lower_stone_base_window",
        "upper": "viking_wall_upper_logs_window",
        "roof": "viking_roof_stone_accent_single",
    },
}
style = styles["viking"]

# FURNITURE TYPES

ONEBYONE_FURNITURE = {
    '1x1_test'
}

TWOBYONE_FURNITURE = {
    '2x1_test'
}

THREEBYONE_FURNITURE = {
    '3x1_test'
}

FOURBYONE_FURNITURE = {
    '4x1_test'
}

FIVEBYONE_FURNITURE = {
    '5x1_test'
}



# PALETTE
palette: Palette = Palette.find("japanese_dark_blackstone")

# WALLS
lower_wall: Wall = Wall.find(style["lower"])
upper_wall: Wall = Wall.find(style["upper"])
interior_wall: Wall = Wall.find('interior_wall')

x_size = 2
y_size = 1
z_size = 2

cells = [ivec3(x, y, z) for x in range(x_size) for y in range(y_size) for z in range(z_size)]


for cell in cells:
    for direction in Directions.Cardinal:
        next = cell + direction
        next_cell = ivec3(next[0], next[1], next[2])
        if next_cell not in cells:
            grid.build(editor, lower_wall, palette, cell, direction)

start = grid.get_door_coords(Directions.North) + grid.grid_to_local(ivec3(0, 0, 0)) + ivec3(0, 0, 1)
print('START: ', start)
editor.placeBlock(start, Block('white_wool'))

def get_neighbours(coords):
    nbrs = []
    for dir in Directions.Cardinal:
        next = coords + dir
        if editor.getBlock(next + Directions.Up).id == 'minecraft:air':
            nbrs.append(next)
    return nbrs

def build_interior_walls(cells: list, floor: int) -> None:
    cells_on_floor = [ivec3(x, y, z) for (x, y, z) in cells if y == floor]
    if len(cells_on_floor) == 1: # no interior walls if there is only 1 cell
        return
    
    elif len(cells_on_floor) == 2: #if there is exactly two cells then let's give it a 50/50 chance for there to be an interior wall
        p = rng.randint(100)
        if p < 50:
            return
        else:
            for cell in cells_on_floor:
                for direction in Directions.Cardinal:
                    next = cell + direction
                    if next in cells_on_floor:
                        grid.build(editor, interior_wall, palette, cell, direction)
                        return
    else:
        #start with a random cell and a random direction
        starting_cell = rng.choose(cells_on_floor)
        possible_directions = []
        for d in Directions.Cardinal:
            next = starting_cell + d
            next = ivec3(next[0], next[1], next[2])
            if next in cells_on_floor:
                possible_directions.append(d)

        starting_direction = rng.choose(possible_directions)
        grid.build(editor, interior_wall, palette, starting_cell, starting_direction)

        #should we connect this wall parallel or perpendicular?
        p = rng.randint(50)
        if p < 50: #parallel
            left = Direction.left(starting_direction)
            next = starting_cell + left
            while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                grid.build(editor, interior_wall, palette, next, starting_direction)
                next = next + left
            right = Direction.right(starting_direction)
            next = starting_cell + right
            while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                grid.build(editor, interior_wall, palette, next, starting_direction)
                next = next + right
            return

        else: #perpendicular
            possible_perp_dir = []
            for d in [Direction.left(starting_direction), Direction.right(starting_direction)]:
                next = starting_cell + d
                next = ivec3(next[0], next[1], next[2])
                if next in cells_on_floor:
                    possible_perp_dir.append(d)
            
            perp_dir = rng.choose(possible_perp_dir)

            next = starting_cell + starting_direction
            while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                grid.build(editor, interior_wall, palette, next, perp_dir)
                next = next + starting_direction                    

            opp = Direction.opposite(starting_direction)
            next = starting_cell + opp
            while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                grid.build(editor, interior_wall, palette, next, perp_dir)
                next = next + opp

        
    
    
def pathfind(start: ivec3, end: ivec3) -> set:
    queue = [(start, 0)]
    visited = set(start)
    parent = {}

    while queue:
        current, dist = queue.pop(0)

        if current == end:
            path = []
            used = set()
            while current != start:
                path.append(current)
                used.add(current)
                used.add(start)
                current = parent[current]
            path.reverse()

            for b in path:
                editor.placeBlock(ivec3(b[0], b[1], b[2]), Block('white_wool'))
                for nbr in get_neighbours(b):
                    used.add(nbr)
                    editor.placeBlock(ivec3(nbr[0], nbr[1], nbr[2]), Block('white_wool'))

            for nbr in get_neighbours(start):
                used.add(nbr)
                editor.placeBlock(ivec3(nbr[0], nbr[1], nbr[2]), Block('white_wool'))
            return used
        
        for nbr in get_neighbours(current):
            if nbr not in visited:
                visited.add(nbr)
                queue.append((nbr, dist + 1))
                parent[nbr] = current

    return set()

def get_corner_type(coords) -> str:
    corners = {
        (False, False, True, True): 'southwest',
        (True, False, False, True): 'northwest',
        (True, True, False, False): 'northeast',
        (False, True, True, False): 'southeast'
    }

    dir_bool = [False, False, False, False]
    for i, dir in enumerate(Directions.Cardinal):
        next = coords + dir
        if editor.getBlock(next + Directions.Up).id != 'minecraft:air':
            dir_bool[i] = True

    return corners[tuple(dir_bool)]

def shift_end_for_stairs(end: ivec3) -> ivec3:
    corner_type = get_corner_type(end)
    match corner_type:
        case 'southwest':
            end = end + ivec3(4, 0, 0)
        case 'northwest': 
            end = end + ivec3(0, 0, 4)
        case 'northeast':
            end = end + ivec3(4, 0, 0)
        case 'southeast':
            end = end + ivec3(0, 0, -4)
        case _:
            return 'Something is wrong with the corner type'
        
    return end

def find_end(start, stairs = True) -> tuple: 
    #find the farthest point
    visited = set(start)
    queue = [(start[0], start[1], start[2], 0)]
    last_visited = None
    while queue:
        headx, heady, headz, steps = queue.pop(0)

        head = (headx, heady, headz)
        last_visited = (head, steps)

        for nbr in get_neighbours(ivec3(head)):
            if nbr not in visited:
                visited.add(nbr)
                queue.append((nbr[0], nbr[1], nbr[2], steps + 1))
    farthest = last_visited[0]
    end = ivec3(farthest[0], farthest[1], farthest[2])
    end_corner_type = get_corner_type(end)

    if stairs:
        end = shift_end_for_stairs(end)

    return end, end_corner_type, visited

def build_stairs(end: ivec3, corner_type: str) -> set:
    stairs = set((ivec3(end[0], end[1], end[2])))
    free_for_stairs = set((ivec3(end[0], end[1], end[2])))
    current = end
    match corner_type:
        case 'southwest':
            for i in range(4):
                current = current + Directions.West
                stairs.add(current)
                editor.placeBlock(ivec3(current[0], current[1], current[2]), Block('orange_wool'))
            
            current = end
            for i in range(2): #this is messy i am sorry
                current = current + Directions.North
                free_for_stairs.add(current)
                editor.placeBlock(ivec3(current[0], current[1], current[2]), Block('white_wool'))
        case 'northwest': 
            for i in range(4):
                current = current + Directions.North
                stairs.add(current)
                editor.placeBlock(ivec3(current[0], current[1], current[2]), Block('orange_wool'))

            current = end    
            for i in range(2): #this is messy i am sorry
                current = current + Directions.East
                free_for_stairs.add(current)
                editor.placeBlock(ivec3(current[0], current[1], current[2]), Block('white_wool'))
        case 'northeast':
            for i in range(4):
                current = current + Directions.East
                stairs.add(current)
                editor.placeBlock(ivec3(current[0], current[1], current[2]), Block('orange_wool'))

            current = end    
            for i in range(2): #this is messy i am sorry
                current = current + Directions.South
                free_for_stairs.add(current)
                editor.placeBlock(ivec3(current[0], current[1], current[2]), Block('white_wool'))
        case 'southeast':
            for i in range(4):
                current = current + Directions.South
                stairs.add(current)
                editor.placeBlock(ivec3(current[0], current[1], current[2]), Block('orange_wool'))

            current = end    
            for i in range(2): #this is messy i am sorry
                current = current + Directions.West
                free_for_stairs.add(current)
                editor.placeBlock(ivec3(current[0], current[1], current[2]), Block('white_wool'))
        case _:
            return 'Something is wrong with the corner type'
        
    return stairs, free_for_stairs

def get_blocks_along_wall(unfilled_blocks: set, stairs_blocks: set, dir: Directions) -> set:
    along_wall = set()
    for block in unfilled_blocks:
        next = block + dir
        if next in stairs_blocks or (editor.getBlock(next + Directions.Up).id != 'minecraft:air' and editor.getBlock(block + Directions.Up + Directions.Up + Directions.Up + Directions.Up).id == 'minecraft:air'):
            along_wall.add(block)

    #probably a terrible solution idk but I need some way to group up these coordinates
    def dfs(start, visited):
        stack = [start]
        group = []
        while stack:
            coord = stack.pop()
            if coord not in visited:
                visited.add(coord)
                group.append(coord)
                for neighbour in get_neighbours(coord):
                    if neighbour in along_wall:
                        stack.append(neighbour)
    
        return group
    
    visited = set()
    groups = []
    for coord in along_wall:
        if coord not in visited:
            group = dfs(coord, visited)
            groups.append(group)

    return groups

def get_leftmost_block(blocks: set, dir: Directions) -> ivec3:
    if dir == Directions.North:
        return min(blocks, key = lambda x: x[0])
    elif dir == Directions.East:
        return min(blocks, key = lambda x: x[2])
    elif dir == Directions.South:
        return max(blocks, key = lambda x: x[0])
    elif dir == Directions.West:
        return max(blocks, key = lambda x: x[2])


def furnish(unfilled_blocks: set, stairs_blocks: set, path_blocks: set) -> None:
    furniture_sizes = [1, 2, 3, 4, 5]
    scores = {5: 5, 4: 4, 3: 3, 2: 2, 1: 1}
    def get_weight(size: int, exact_fit: bool) -> int:
        if exact_fit:
            return scores[size] + 5
        return scores[size]
    
    def plan_furniture(length: int) -> list:
        if length == 0:
            return []
        
        best_plan = None
        weights = {}

        for size in furniture_sizes:
            if size <= length:
                exact_fit = size == length
                weight = get_weight(size, exact_fit)
                weights[size] = weight

        selected_size = rng.choose_weighted(weights)
        remaining_length = length - selected_size
        remaining_plan = plan_furniture(remaining_length)
        best_plan = [selected_size] + remaining_plan

        return best_plan


    #from all of the unfilled blocks to be furnished, we want to start by filling in the largest space first
    def furnish_along_wall(unfilled_blocks: set, stairs_blocks: set) -> set:
        longest = 0
        for dir in Directions.Cardinal:
            blocks_along_dir_wall = get_blocks_along_wall(unfilled_blocks, stairs_blocks, dir)
            for group in blocks_along_dir_wall:
                if len(group) >= longest:
                    longest = len(group)
                    longest_dir = dir


        along_wall_groups = get_blocks_along_wall(unfilled_blocks, stairs_blocks, longest_dir)
        if not blocks_along_dir_wall:
            return None
        
        blocks_along_dir_wall = max(along_wall_groups, key = len)


        
        #how do we split up the furniture along the wall
        plan =  plan_furniture(len(blocks_along_dir_wall))
        
        #testing for now but I furniture placement NBT goes here
        leftmost_block_along_wall = get_leftmost_block(blocks_along_dir_wall, longest_dir)
    
        colours_for_testing = {
            1: 'red_wool',
            2: 'light_blue_wool',
            3: 'yellow_wool',
            4: 'lime_wool',
            5: 'blue_wool'
        }

        current = leftmost_block_along_wall
        for p in plan:
            match p:
                case 1:
                    furniture_choice = rng.choose(ONEBYONE_FURNITURE)
                case 2:
                    furniture_choice = rng.choose(TWOBYONE_FURNITURE)
                case 3:
                    furniture_choice = rng.choose(THREEBYONE_FURNITURE)
                case 4:
                    furniture_choice = rng.choose(FOURBYONE_FURNITURE)
                case 5:
                    furniture_choice = rng.choose(FIVEBYONE_FURNITURE)
                case _:
                    print('We dont have furniture for that size!')
                    return
                
            furniture: Room = Room.find(furniture_choice) #techincally should be a different type than Room but not worried about it rn
            build_nbt(editor, furniture, palette, )

            for x in range(p):
                editor.placeBlock(ivec3(current[0], current[1], current[2]), Block(colours_for_testing[p]))
                current = current + Direction.right(longest_dir)

        for block in blocks_along_dir_wall:
            unfilled_blocks.discard(block)
            block_infront = block + Direction.opposite(longest_dir)
            if block_infront in unfilled_blocks:
                unfilled_blocks.discard(block_infront)

        return unfilled_blocks
    
    while unfilled_blocks is not None:
        unfilled_blocks = furnish_along_wall(unfilled_blocks, stairs_blocks)

    return
    
    
for floor in range(y_size):
    build_interior_walls(cells, floor)                                                                                      
end, end_corner_type, floor_space = find_end(start, stairs = True)
path = set(end)
#path = pathfind(start, end)
stairs_blocks, free_for_stairs = build_stairs(end, end_corner_type)
filled = path.union(stairs_blocks)
filled = filled.union(free_for_stairs)
filled.add(end)

to_fill = floor_space.difference(filled)
to_fill = {item for item in to_fill if not isinstance(item, int)}

for block in to_fill: 
    if ivec3(block[0], block[1], block[2]) == end:
        x = block
to_fill.remove(x)

for block in to_fill:
    editor.placeBlock((block[0], block[1], block[2]), Block('black_wool'))


furnish(to_fill, stairs_blocks, path)

# ROOF
roof: Roof = Roof.find(style["roof"])
# roof.build(editor, palette, grid, (0, 2, 0))