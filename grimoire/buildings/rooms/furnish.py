# Actual file
from gdpc.editor import Editor, Block
from grimoire.core.structures.grid import Grid
from grimoire.core.styling.palette import Palette
from grimoire.buildings.walls.wall import Wall
from grimoire.core.structures import legacy_directions
from grimoire.core.structures.transformation import Transformation
from grimoire.buildings.rooms.furniture import Furniture
from grimoire.core.structures.nbt.nbt_asset import NBTAsset
from grimoire.core.structures.nbt.build_nbt import build_nbt
from grimoire.core.assets.asset_loader import load_assets
from gdpc.vector_tools import CARDINALS, NORTH, EAST, SOUTH, WEST, UP, rotate3D
from gdpc.vector_tools import ivec3
from grimoire.core.noise.rng import RNG

def get_neighbours(coords: ivec3, editor: Editor):
    nbrs = []
    for dir in CARDINALS:
        next = coords + dir
        if editor.getBlock(next + UP).id == 'minecraft:air':
            nbrs.append(next)
    return nbrs

def build_interior_walls(cells: list, floor: int, palette: Palette, editor: Editor, grid: Grid, rng: RNG) -> None:
    interior_wall: Wall = Wall.find('interior_wall')

    cells_on_floor = [ivec3(x, y, z) for (x, y, z) in cells if y == floor]
    if len(cells_on_floor) == 1: # no interior walls if there is only 1 cell
        return
    
    elif len(cells_on_floor) == 2: #if there is exactly two cells then let's give it a 50/50 chance for there to be an interior wall
        p = rng.randint(100)
        if p < 50:
            return
        else:
            for cell in cells_on_floor:
                for direction in CARDINALS:
                    next = cell + direction
                    if next in cells_on_floor:
                        grid.build(editor, interior_wall, palette, cell, direction)
                        return
    else:
        #start with a random cell and a random direction
        starting_cell = rng.choose(cells_on_floor)
        possible_directions = []
        for d in CARDINALS:
            next = starting_cell + d
            next = ivec3(next[0], next[1], next[2])
            if next in cells_on_floor:
                possible_directions.append(d)

        if not possible_directions:
            return

        starting_direction = rng.choose(possible_directions)
        grid.build(editor, interior_wall, palette, starting_cell, starting_direction)

        #should we connect this wall parallel or perpendicular?
        p = rng.randint(50)
        if p < 50: #parallel
            left = rotate3D(starting_direction, 3)
            next = starting_cell + left
            while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                grid.build(editor, interior_wall, palette, next, starting_direction)
                next = next + left
            right = rotate3D(starting_direction, 1)
            next = starting_cell + right
            while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                grid.build(editor, interior_wall, palette, next, starting_direction)
                next = next + right
            return

        else: #perpendicular
            possible_perp_dir = []
            for d in [rotate3D(starting_direction, 3), rotate3D(starting_direction, 1)]:
                next = starting_cell + d
                next = ivec3(next[0], next[1], next[2])
                if next in cells_on_floor:
                    possible_perp_dir.append(d)
            
            perp_dir = rng.choose(possible_perp_dir)

            next = starting_cell + starting_direction
            while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                grid.build(editor, interior_wall, palette, next, perp_dir)
                next = next + starting_direction                    

            opp = rotate3D(starting_direction, 2)
            next = starting_cell + opp
            while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                grid.build(editor, interior_wall, palette, next, perp_dir)
                next = next + opp
    
def pathfind(start: ivec3, end: ivec3, editor: Editor) -> set:
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
                for nbr in get_neighbours(b, editor):
                    used.add(nbr)

            for nbr in get_neighbours(start, editor):
                used.add(nbr)
            return used
        
        for nbr in get_neighbours(current, editor):
            if nbr not in visited:
                visited.add(nbr)
                queue.append((nbr, dist + 1))
                parent[nbr] = current

    return set()

def get_corner_type(coords: ivec3, editor: Editor) -> str:
    corners = {
        (False, False, True, True): 'southwest',
        (True, False, False, True): 'northwest',
        (True, True, False, False): 'northeast',
        (False, True, True, False): 'southeast'
    }

    dir_bool = [False, False, False, False]
    for i, dir in enumerate(CARDINALS):
        next = coords + dir
        if editor.getBlock(next + UP).id != 'minecraft:air':
            dir_bool[i] = True

    if tuple(dir_bool) in corners:
        return corners[tuple(dir_bool)]
    else:
        return 'northwest'



def shift_end_for_stairs(end: ivec3, editor: Editor) -> ivec3:
    corner_type = get_corner_type(end, editor)
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

def find_end(start: ivec3, stairs: bool, editor: Editor) -> tuple: 
    #find the farthest point
    visited = set(start)
    queue = [(start[0], start[1], start[2], 0)]
    last_visited = None
    while queue:
        headx, heady, headz, steps = queue.pop(0)

        head = (headx, heady, headz)
        last_visited = (head, steps)

        for nbr in get_neighbours(ivec3(head), editor):
            if nbr not in visited:
                visited.add(nbr)
                queue.append((nbr[0], nbr[1], nbr[2], steps + 1))
    farthest = last_visited[0]
    end = ivec3(farthest[0], farthest[1], farthest[2])
    end_corner_type = get_corner_type(end, editor)

    if stairs:
        end = shift_end_for_stairs(end, editor)

    return end, end_corner_type, visited

def build_stairs(end: ivec3, corner_type: str, floor_height: int, palette: Palette, editor: Editor) -> set:
    stairs = set((ivec3(end[0], end[1], end[2])))
    stairs_nbt: NBTAsset = NBTAsset.find('interior_stairs')
    free_for_stairs = set((ivec3(end[0], end[1], end[2])))
    current = end
    match corner_type:
        case 'southwest':
            for i in range(4):
                current = current + WEST
                stairs.add(current)
                editor.placeBlock(current + UP * floor_height, Block(id = 'minecraft:air'))

            build_nbt(
                editor,
                stairs_nbt,
                palette,
                Transformation( 
                    offset= end + WEST + ivec3(0, 1, 0),
                    rotations = 1
                ),
                material_params_func=None,
                build_map=None,
            )

            current = end
            for i in range(2): #this is messy i am sorry
                current = current + NORTH
                free_for_stairs.add(current)
        case 'northwest': 
            for i in range(4):
                current = current + NORTH
                stairs.add(current)
                editor.placeBlock(current + UP * floor_height, Block(id = 'minecraft:air'))

            build_nbt(
                editor,
                stairs_nbt,
                palette,
                Transformation( 
                    offset= end + NORTH + ivec3(0, 1, 0),
                    rotations = 2
                ),
                material_params_func=None,
                build_map=None,
            )
            current = end    
            for i in range(2): #this is messy i am sorry
                current = current + EAST
                free_for_stairs.add(current)
        case 'northeast':
            for i in range(4):
                current = current + EAST
                stairs.add(current)
                editor.placeBlock(current + UP * floor_height, Block(id = 'minecraft:air'))

            build_nbt(
                editor,
                stairs_nbt,
                palette,
                Transformation( 
                    offset= end + EAST + ivec3(0, 1, 0),
                    rotations = 3
                ),
                material_params_func=None,
                build_map=None,
            )

            current = end    
            for i in range(2): #this is messy i am sorry
                current = current + SOUTH
                free_for_stairs.add(current)
        case 'southeast':
            for i in range(4):
                current = current + SOUTH
                stairs.add(current)
                editor.placeBlock(current + UP * floor_height, Block(id = 'minecraft:air'))

            build_nbt(
                editor,
                stairs_nbt,
                palette,
                Transformation( 
                    offset= end + SOUTH + ivec3(0, 1, 0),
                ),
                material_params_func=None,
                build_map=None,
            )

            current = end    
            for i in range(2): #this is messy i am sorry
                current = current + WEST
                free_for_stairs.add(current)
        case _:
            return 'Something is wrong with the corner type'
        
    return stairs, free_for_stairs

def get_blocks_along_wall(unfilled_blocks: set, stairs_blocks: set, dir: ivec3, editor: Editor) -> set:
    along_wall = set()
    for block in unfilled_blocks:
        next = block + dir
        if next in stairs_blocks or (editor.getBlock(next + UP).id != 'minecraft:air' and editor.getBlock(block + UP * 4).id == 'minecraft:air'):
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
                for neighbour in get_neighbours(coord, editor):
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

def get_leftmost_block(blocks: set, dir: ivec3) -> ivec3:
    if dir == NORTH:
        return min(blocks, key = lambda x: x[0])
    elif dir == EAST:
        return min(blocks, key = lambda x: x[2])
    elif dir == SOUTH:
        return max(blocks, key = lambda x: x[0])
    elif dir == WEST:
        return max(blocks, key = lambda x: x[2])


def furnish(unfilled_blocks: set, stairs_blocks: set, path_blocks: set, palette: Palette, editor: Editor, grid: Grid, rng: RNG) -> None:

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
    def furnish_along_wall(unfilled_blocks: set, stairs_blocks: set, editor: Editor) -> set:
        longest = 0
        longest_dir = None
        for dir in CARDINALS:
            blocks_along_dir_wall = get_blocks_along_wall(unfilled_blocks, stairs_blocks, dir, editor)
            for group in blocks_along_dir_wall:
                if len(group) >= longest:
                    longest = len(group)
                    longest_dir = dir

        if longest_dir is None:
            return

        along_wall_groups = get_blocks_along_wall(unfilled_blocks, stairs_blocks, longest_dir, editor)
        if not blocks_along_dir_wall:
            return None
        
        blocks_along_dir_wall = max(along_wall_groups, key = len)

        #how do we split up the furniture along the wall
        plan =  plan_furniture(len(blocks_along_dir_wall))
        
        #testing for now but I furniture placement NBT goes here
        leftmost_block_along_wall = get_leftmost_block(blocks_along_dir_wall, longest_dir)

        current = leftmost_block_along_wall

        for subdivision in plan:
            furniture = rng.choose(list(furniture for furniture in Furniture.all() if furniture.length == subdivision))
            
            if legacy_directions.VECTORS[furniture.facing] == longest_dir:
                build_nbt(
                    editor,
                    furniture,
                    palette,
                    Transformation(
                        offset=current + ivec3(0, 1, 0),
                    ),
                    material_params_func=None,
                    build_map=None,
                )

            if rotate3D(legacy_directions.VECTORS[furniture.facing], 1) == longest_dir:
                build_nbt(
                    editor,
                    furniture,
                    palette,
                    Transformation(
                        offset=current + ivec3(0, 1, 0),
                        rotations = 1
                    ),
                    material_params_func=None,
                    build_map=None,
                )

            if rotate3D(legacy_directions.VECTORS[furniture.facing], 3) == longest_dir:
                build_nbt(
                    editor,
                    furniture,
                    palette,
                    Transformation(
                        rotations = 3,
                        offset=current + ivec3(0, 1,0),
                    ),
                    material_params_func=None,
                    build_map=None,
                )

            if rotate3D(legacy_directions.VECTORS[furniture.facing], 2) == longest_dir:
                build_nbt(
                    editor,
                    furniture,
                    palette,
                    Transformation(
                        rotations = 2,
                        offset=current + ivec3(0, 1, 0),
                    ),
                    material_params_func=None,
                    build_map=None,
                )
            current = current + subdivision * rotate3D(longest_dir, 1) 

        for block in blocks_along_dir_wall:
            unfilled_blocks.discard(block)
            block_infront = block + rotate3D(longest_dir, 2)
            if block_infront in unfilled_blocks:
                unfilled_blocks.discard(block_infront)

        return unfilled_blocks
    
    while unfilled_blocks is not None:
        unfilled_blocks = furnish_along_wall(unfilled_blocks, stairs_blocks, editor)

    return
    
def furnish_building(cells: list, door_coords: ivec3, palette: Palette, editor: Editor, grid: Grid, rng: RNG):
    num_floors = max(cells, key = lambda x: x[1]).y + 1
    floor_height = (grid.origin + grid.grid_to_local(ivec3(0, 1, 0))).y
    stairs_blocks = set()
    end_corner_type = None

    for floor in range(num_floors):
        if floor == 0:
            start = door_coords
            filled = set(start)
        else:
            stairs_blocks = {item for item in stairs_blocks if not isinstance(item, int)}
            if end_corner_type == 'northeast':
                start = max(stairs_blocks, key = lambda x: x[0]) + SOUTH + ivec3(0, floor_height, 0)
            elif end_corner_type == 'southeast':
                start = max(stairs_blocks, key = lambda x: x[2]) + WEST + ivec3(0, floor_height, 0)
            elif end_corner_type == 'southwest':
                start = min(stairs_blocks, key = lambda x: x[0]) + NORTH + ivec3(0, floor_height, 0)
            elif end_corner_type == 'northwest':
                start = min(stairs_blocks, key = lambda x: x[2]) + EAST + ivec3(0, floor_height, 0)

            filled = {ivec3(x, y + floor_height, z) for (x, y, z) in stairs_blocks}
            filled.add(start)
            
        build_interior_walls(cells, floor, palette, editor, grid, rng)
        if floor == num_floors - 1:
            has_stairs = False
            end, end_corner_type, floor_space = find_end(start, has_stairs, editor)
            path = set(end)
            filled = filled.union(path)
        else:
            has_stairs = True
            end, end_corner_type, floor_space = find_end(start, has_stairs, editor)
            path = set(end)
            stairs_blocks, free_for_stairs = build_stairs(end, end_corner_type, floor_height, palette, editor)
            filled = filled.union(path)
            filled = filled.union(stairs_blocks)
            filled = filled.union(free_for_stairs)
            filled.add(end)

        to_fill = floor_space.difference(filled)    
        to_fill = {item for item in to_fill if not isinstance(item, int)}
        if start in to_fill:
            to_fill.remove(start)

        furnish(to_fill, stairs_blocks, path, palette, editor, grid, rng)