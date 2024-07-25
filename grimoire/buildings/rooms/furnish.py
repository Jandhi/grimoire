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
from gdpc.vector_tools import ivec3, dropY, addY
from grimoire.core.noise.rng import RNG
from grimoire.core.utils.sets.find_outer_points import find_edges_2D, find_edges_3D


def get_neighbours(coords: ivec3, editor: Editor):
    nbrs = []
    for dir in CARDINALS:
        next = coords + dir
        if editor.getBlock(next + UP).id == "minecraft:air":
            nbrs.append(next)
    return nbrs


def get_blocks_along_dir_of_cell(cell: ivec3, direction: ivec3, grid: Grid) -> set:
    blocks_along_cell_dir = set()
    bottom_left_block = grid.grid_to_world(cell) + UP
    x_dim = grid.dimensions.x
    z_dim = grid.dimensions.z
    if direction == NORTH:
        current = bottom_left_block + NORTH * (z_dim - 1)
        for i in range(x_dim):
            blocks_along_cell_dir.add(current)
            current = current + EAST
    elif direction == EAST:
        current = bottom_left_block + EAST * (x_dim - 1)
        for i in range(z_dim):
            blocks_along_cell_dir.add(current)
            current = current + NORTH
    elif direction == SOUTH:
        current = bottom_left_block
        for i in range(x_dim):
            blocks_along_cell_dir.add(current)
            current = current + EAST
    elif direction == WEST:
        current = bottom_left_block
        for i in range(z_dim):
            blocks_along_cell_dir.add(current)
            current = current + NORTH

    return blocks_along_cell_dir


def build_interior_walls(
    cells: list, floor: int, palette: Palette, editor: Editor, grid: Grid, rng: RNG
) -> set:
    interior_wall: Wall = Wall.find("interior_wall")
    interior_wall_cells = set()

    cells_on_floor = [ivec3(x, y, z) for (x, y, z) in cells if y == floor]
    if len(cells_on_floor) == 1:  # no interior walls if there is only 1 cell
        return set()

    elif (
        len(cells_on_floor) == 2
    ):  # if there is exactly two cells then let's give it a 50/50 chance for there to be an interior wall
        p = rng.randint(100)
        if p < 50:
            return None
        else:
            for cell in cells_on_floor:
                for direction in CARDINALS:
                    next = cell + direction
                    if next in cells_on_floor:
                        grid.build(editor, interior_wall, palette, cell, direction)
                        interior_wall_cells.add((cell, direction))
                        return interior_wall_cells
    else:
        # start with a random cell and a random direction
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
        interior_wall_cells.add((starting_cell, starting_direction))

        # should we connect this wall parallel or perpendicular?
        p = rng.randint(50)
        if p < 50:  # parallel
            left = rotate3D(starting_direction, 3)
            next = starting_cell + left
            while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                grid.build(editor, interior_wall, palette, next, starting_direction)
                interior_wall_cells.add((next, starting_direction))
                next = next + left
            right = rotate3D(starting_direction, 1)
            next = starting_cell + right
            while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                grid.build(editor, interior_wall, palette, next, starting_direction)
                interior_wall_cells.add((next, starting_direction))
                next = next + right

        else:  # perpendicular
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
                interior_wall_cells.add((next, perp_dir))
                next = next + starting_direction

            opp = rotate3D(starting_direction, 2)
            next = starting_cell + opp
            while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                grid.build(editor, interior_wall, palette, next, perp_dir)
                interior_wall_cells.add((next, perp_dir))
                next = next + opp
        if len(cells_on_floor) > 4:
            # start with a random cell and a random direction
            starting_cell = rng.choose(
                [c for c in cells_on_floor if c != starting_cell]
            )
            possible_directions = []
            for d in [d for d in CARDINALS if d != starting_direction]:
                next = starting_cell + d
                next = ivec3(next[0], next[1], next[2])
                if next in cells_on_floor:
                    possible_directions.append(d)

            if not possible_directions:
                return

            starting_direction = rng.choose(possible_directions)
            grid.build(
                editor, interior_wall, palette, starting_cell, starting_direction
            )
            interior_wall_cells.add((starting_cell, starting_direction))

            # should we connect this wall parallel or perpendicular?
            p = rng.randint(50)
            if p < 50:  # parallel
                left = rotate3D(starting_direction, 3)
                next = starting_cell + left
                while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                    grid.build(editor, interior_wall, palette, next, starting_direction)
                    interior_wall_cells.add((next, starting_direction))
                    next = next + left
                right = rotate3D(starting_direction, 1)
                next = starting_cell + right
                while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                    grid.build(editor, interior_wall, palette, next, starting_direction)
                    interior_wall_cells.add((next, starting_direction))
                    next = next + right

            else:  # perpendicular
                possible_perp_dir = []
                for d in [
                    rotate3D(starting_direction, 3),
                    rotate3D(starting_direction, 1),
                ]:
                    next = starting_cell + d
                    next = ivec3(next[0], next[1], next[2])
                    if next in cells_on_floor:
                        possible_perp_dir.append(d)

                perp_dir = rng.choose(possible_perp_dir)

                next = starting_cell + starting_direction
                while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                    grid.build(editor, interior_wall, palette, next, perp_dir)
                    interior_wall_cells.add((next, perp_dir))
                    next = next + starting_direction

                opp = rotate3D(starting_direction, 2)
                next = starting_cell + opp
                while ivec3(next[0], next[1], next[2]) in cells_on_floor:
                    grid.build(editor, interior_wall, palette, next, perp_dir)
                    interior_wall_cells.add((next, perp_dir))
                    next = next + opp

    return interior_wall_cells


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


def get_corner_type(coords: ivec3, grid: Grid, cells: list) -> str:
    corner_types = {
        (False, False, True, True): "southwest",
        (True, False, False, True): "northwest",
        (True, True, False, False): "northeast",
        (False, True, True, False): "southeast",
    }

    grid_pos = grid.world_to_grid(coords)
    dir_bool = [False, False, False, False]
    for i, dir in enumerate(CARDINALS):
        next = grid_pos + dir
        if next not in cells:
            dir_bool[i] = True

    if tuple(dir_bool) in corner_types:
        return corner_types[tuple(dir_bool)]
    else:
        return None


def get_cubby_type(coords: ivec3, grid: Grid, cells: list) -> str:
    cubby_types = {
        (False, True, True, True): "north",
        (True, False, True, True): "east",
        (True, True, False, True): "south",
        (True, True, True, False): "west",
    }
    grid_pos = grid.world_to_grid(coords)
    dir_bool = [False, False, False, False]
    for i, dir in enumerate(CARDINALS):
        next = grid_pos + dir
        if next not in cells:
            dir_bool[i] = True

    if tuple(dir_bool) in cubby_types:
        return cubby_types[tuple(dir_bool)]
    else:
        return None


def shift_end_for_stairs(
    end: ivec3, grid: Grid, cells: list, corner_type: str
) -> ivec3:
    match corner_type:
        case "southwest":
            end = end + ivec3(4, 0, 0)
        case "northwest":
            end = end + ivec3(0, 0, 4)
        case "northeast":
            end = end + ivec3(-4, 0, 0)
        case "southeast":
            end = end + ivec3(0, 0, -4)
        case _:
            return "Something is wrong with the corner type"

    return end


def distance(c1: ivec3, c2: ivec3) -> float:
    return ((c1[0] - c2[0]) ** 2 + (c1[2] - c2[2]) ** 2) ** 0.5


def get_wall_type(coords: ivec3, grid, cells) -> str:
    # these should be just north east south or west but I'm gonna make these match the corner types for to save time. I was always placing the end on the corner so 'southeast' means an east wall for example
    wall_types = {
        (True, False, False, False): "northeast",
        (False, True, False, False): "southeast",
        (False, False, True, False): "southwest",
        (False, False, False, True): "northwest",
    }

    grid_pos = grid.world_to_grid(coords)
    dir_bool = [False, False, False, False]
    for i, dir in enumerate(CARDINALS):
        next = grid_pos + dir
        if next not in cells:
            dir_bool[i] = True

    if tuple(dir_bool) in wall_types:
        return wall_types[tuple(dir_bool)]
    else:
        return None


def map_inside_area(grid: Grid, cells: list, floor: int):
    cells_on_floor = [ivec3(x, y, z) for (x, y, z) in cells if y == floor]
    points = set()
    for cell in cells_on_floor:
        points |= set(grid.get_points_at_2d(dropY(cell)))

    for point in find_edges_2D(points):
        points.remove(point)

    y_val = grid.grid_to_world(ivec3(0, floor, 0)).y + 1

    return {addY(point, y_val) for point in points}


def find_end(
    start: ivec3,
    cells: list,
    has_stairs: bool,
    floor: int,
    editor: Editor,
    grid: Grid,
    rng: RNG,
    filled: set,
    door_dir: ivec3,
) -> tuple:
    max_floor = max(cells, key=lambda x: x[1]).y

    start_cell = grid.world_to_grid(start)
    inside_map = map_inside_area(grid, cells, floor)

    cells_on_floor = {ivec3(x, y, z) for (x, y, z) in cells if y == floor}
    if len(cells_on_floor) == 1:
        only_cell = cells_on_floor.pop()
        bottom_left_block = grid.grid_to_world(only_cell)
        cell_corners = [
            ivec3(
                bottom_left_block[0] + 1, bottom_left_block[1], bottom_left_block[2] + 1
            ),
            ivec3(
                bottom_left_block[0] + 1 + grid.dimensions.x - 3,
                bottom_left_block[1],
                bottom_left_block[2] + 1,
            ),
            ivec3(
                bottom_left_block[0] + 1,
                bottom_left_block[1],
                bottom_left_block[2] + 1 + grid.dimensions.z - 3,
            ),
            ivec3(
                bottom_left_block[0] + 1 + grid.dimensions.x - 3,
                bottom_left_block[1],
                bottom_left_block[2] + 1 + grid.dimensions.z - 3,
            ),
        ]
        if floor == max_floor and not has_stairs:
            end = max(cell_corners, key=lambda c: distance(start, c))
            end_corner_type = "northwest"
            return end, end_corner_type, inside_map
        else:
            if door_dir == NORTH:
                end = min(cell_corners, key=lambda c: (c[0], -c[2]))
                end_corner_type = "southwest"
                end = shift_end_for_stairs(end, grid, cells, end_corner_type)
                return end, end_corner_type, inside_map
            elif door_dir == EAST:
                end = min(cell_corners, key=lambda c: (c[0], c[2]))
                end_corner_type = "northwest"
                end = shift_end_for_stairs(end, grid, cells, end_corner_type)
                return end, end_corner_type, inside_map
            elif door_dir == WEST:
                end = min(cell_corners, key=lambda c: (-c[0], -c[2]))
                end_corner_type = "southeast"
                end = shift_end_for_stairs(end, grid, cells, end_corner_type)
                return end, end_corner_type, inside_map
            elif door_dir == SOUTH:
                end = min(cell_corners, key=lambda c: (-c[0], c[2]))
                end_corner_type = "northeast"
                end = shift_end_for_stairs(end, grid, cells, end_corner_type)
                return end, end_corner_type, inside_map

    else:
        if floor == max_floor:
            farthest_cell = max(cells_on_floor, key=lambda c: distance(start_cell, c))
            farthest_block = grid.grid_to_world(farthest_cell)
            cell_corners = [
                ivec3(farthest_block[0] + 1, farthest_block[1], farthest_block[2] + 1),
                ivec3(
                    farthest_block[0] + 1 + grid.dimensions.x - 3,
                    farthest_block[1],
                    farthest_block[2] + 1,
                ),
                ivec3(
                    farthest_block[0] + 1,
                    farthest_block[1],
                    farthest_block[2] + 1 + grid.dimensions.z - 3,
                ),
                ivec3(
                    farthest_block[0] + 1 + grid.dimensions.x - 3,
                    farthest_block[1],
                    farthest_block[2] + 1 + grid.dimensions.z - 3,
                ),
            ]
            end = farthest_block
            cell_corner_type = get_corner_type(farthest_block, grid, cells)
            if cell_corner_type == "northwest":
                end = min(cell_corners, key=lambda c: (c[0], c[2]))
            elif cell_corner_type == "northeast":
                end = min(cell_corners, key=lambda c: (-c[0], c[2]))
            elif cell_corner_type == "southeast":
                end = min(cell_corners, key=lambda c: (-c[0], -c[2]))
            elif cell_corner_type == "southwest":
                end = min(cell_corners, key=lambda c: (c[0], -c[2]))

            end_corner_type = get_corner_type(end, grid, cells)
            return end, end_corner_type, inside_map
        else:  # we need to build stairs
            cell_set = set(cells)
            overlapping_cells = {
                ivec3(x, y, z)
                for (x, y, z) in cell_set
                if y == floor and ivec3(x, y + 1, z) in cell_set
            }
            farthest_cell = max(
                overlapping_cells, key=lambda c: distance(start_cell, c)
            )
            farthest_block = grid.grid_to_world(farthest_cell)
            cell_corners = [
                ivec3(farthest_block[0] + 1, farthest_block[1], farthest_block[2] + 1),
                ivec3(
                    farthest_block[0] + 1 + grid.dimensions.x - 3,
                    farthest_block[1],
                    farthest_block[2] + 1,
                ),
                ivec3(
                    farthest_block[0] + 1,
                    farthest_block[1],
                    farthest_block[2] + 1 + grid.dimensions.z - 3,
                ),
                ivec3(
                    farthest_block[0] + 1 + grid.dimensions.x - 3,
                    farthest_block[1],
                    farthest_block[2] + 1 + grid.dimensions.z - 3,
                ),
            ]

            cell_corner_type = get_corner_type(farthest_block, grid, cells)
            if cell_corner_type is None:  # we have a cubby
                cubby_type = get_cubby_type(farthest_block, grid, cells)
                if cubby_type == "north":
                    end = min(cell_corners, key=lambda c: (c[0], -c[2]))
                    end_corner_type = "southwest"
                    end = shift_end_for_stairs(end, grid, cells, end_corner_type)
                    return end, end_corner_type, inside_map
                elif cubby_type == "east":
                    end = min(cell_corners, key=lambda c: (c[0], c[2]))
                    end_corner_type = "northwest"
                    end = shift_end_for_stairs(end, grid, cells, end_corner_type)
                    return end, end_corner_type, inside_map
                elif cubby_type == "west":
                    end = min(cell_corners, key=lambda c: (-c[0], -c[2]))
                    end_corner_type = "southeast"
                    end = shift_end_for_stairs(end, grid, cells, end_corner_type)
                    return end, end_corner_type, inside_map
                elif cubby_type == "south":
                    end = min(cell_corners, key=lambda c: (-c[0], c[2]))
                    end_corner_type = "northeast"
                    end = shift_end_for_stairs(end, grid, cells, end_corner_type)
                    return end, end_corner_type, inside_map
            else:  # we are at a corner in the house
                if cell_corner_type == "northwest":
                    end = min(cell_corners, key=lambda c: (c[0], c[2]))
                elif cell_corner_type == "northeast":
                    end = min(cell_corners, key=lambda c: (-c[0], c[2]))
                elif cell_corner_type == "southeast":
                    end = min(cell_corners, key=lambda c: (-c[0], -c[2]))
                elif cell_corner_type == "southwest":
                    end = min(cell_corners, key=lambda c: (c[0], -c[2]))

                end_corner_type = cell_corner_type
                end = shift_end_for_stairs(end, grid, cells, end_corner_type)
                return end, end_corner_type, inside_map


def build_stairs(
    end: ivec3, corner_type: str, floor_height: int, palette: Palette, editor: Editor
) -> tuple:
    stairs = set()
    stairs.add(end)
    stairs_nbt: NBTAsset = NBTAsset.find("interior_stairs")
    free_for_stairs = set()
    free_for_stairs.add(end)
    current = end
    match corner_type:
        case "southwest":
            for i in range(4):
                current = current + WEST
                stairs.add(current)
                editor.placeBlock(current + UP * 3, Block(id="minecraft:air"))

            build_nbt(
                editor,
                stairs_nbt,
                palette,
                Transformation(offset=end + WEST, rotations=1),
                material_params_func=None,
                build_map=None,
            )

            current = end
            for i in range(2):  # this is messy i am sorry
                current = current + NORTH
                free_for_stairs.add(current)
        case "northwest":
            for i in range(4):
                current = current + NORTH
                stairs.add(current)
                editor.placeBlock(current + UP * 3, Block(id="minecraft:air"))

            build_nbt(
                editor,
                stairs_nbt,
                palette,
                Transformation(offset=end + NORTH, rotations=2),
                material_params_func=None,
                build_map=None,
            )

            current = end
            for i in range(2):  # this is messy i am sorry
                current = current + EAST
                free_for_stairs.add(current)
        case "northeast":
            for i in range(4):
                current = current + EAST
                stairs.add(current)
                editor.placeBlock(current + UP * 3, Block(id="minecraft:air"))

            build_nbt(
                editor,
                stairs_nbt,
                palette,
                Transformation(offset=end + EAST, rotations=3),
                material_params_func=None,
                build_map=None,
            )

            current = end
            for i in range(2):  # this is messy i am sorry
                current = current + SOUTH
                free_for_stairs.add(current)
        case "southeast":
            for i in range(4):
                current = current + SOUTH
                stairs.add(current)
                editor.placeBlock(current + UP * 3, Block(id="minecraft:air"))

            build_nbt(
                editor,
                stairs_nbt,
                palette,
                Transformation(
                    offset=end + SOUTH,
                ),
                material_params_func=None,
                build_map=None,
            )
            current = end
            for i in range(2):  # this is messy i am sorry
                current = current + WEST
                free_for_stairs.add(current)
        case _:
            return "Something is wrong with the corner type"

    return stairs, free_for_stairs


def get_blocks_along_wall(
    footprint: set, filled: set, dir: ivec3, editor: Editor
) -> set:
    along_wall = set()

    for block in footprint:
        if block + dir not in footprint and block not in filled:
            along_wall.add(block)

    def dfs(start, visited):
        stack = [start]
        group = []
        while stack:
            coord = stack.pop()
            if coord not in visited:
                visited.add(coord)
                group.append(coord)
                for direction in CARDINALS:
                    neighbor = coord + direction
                    if neighbor in along_wall:
                        stack.append(neighbor)

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
        return min(blocks, key=lambda x: x[0])
    elif dir == EAST:
        return min(blocks, key=lambda x: x[2])
    elif dir == SOUTH:
        return max(blocks, key=lambda x: x[0])
    elif dir == WEST:
        return max(blocks, key=lambda x: x[2])


def furnish(
    footprint: set,
    filled: set,
    stairs_blocks: set,
    path_blocks: set,
    palette: Palette,
    editor: Editor,
    grid: Grid,
    rng: RNG,
) -> None:
    furniture_sizes = [1, 2, 3, 4, 5]
    scores = {5: 5, 4: 4, 3: 3, 2: 2, 1: 1}
    placeable = find_edges_3D(footprint)

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

    # from all of the unfilled blocks to be furnished, we want to start by filling in the largest space first
    def furnish_along_wall(
        footprint: set, filled: set, stairs_blocks: set, editor: Editor
    ) -> set:
        longest = 0
        longest_dir = None
        for dir in CARDINALS:
            blocks_along_dir_wall = get_blocks_along_wall(
                footprint, filled, dir, editor
            )
            for group in blocks_along_dir_wall:
                if len(group) >= longest:
                    longest = len(group)
                    longest_dir = dir

        if longest_dir is None:
            return

        along_wall_groups = get_blocks_along_wall(
            footprint, filled, longest_dir, editor
        )
        if not blocks_along_dir_wall:
            return None

        blocks_along_dir_wall = max(along_wall_groups, key=len)

        # how do we split up the furniture along the wall
        plan = plan_furniture(len(blocks_along_dir_wall))

        # testing for now but I furniture placement NBT goes here
        leftmost_block_along_wall = get_leftmost_block(
            blocks_along_dir_wall, longest_dir
        )

        current = leftmost_block_along_wall

        for subdivision in plan:
            furniture = rng.choose(
                list(
                    furniture
                    for furniture in Furniture.all()
                    if furniture.length == subdivision
                )
            )

            if legacy_directions.VECTORS[furniture.facing] == longest_dir:
                build_nbt(
                    editor,
                    furniture,
                    palette,
                    Transformation(
                        offset=current,
                    ),
                    material_params_func=None,
                    build_map=None,
                )

            if rotate3D(legacy_directions.VECTORS[furniture.facing], 1) == longest_dir:
                build_nbt(
                    editor,
                    furniture,
                    palette,
                    Transformation(offset=current, rotations=1),
                    material_params_func=None,
                    build_map=None,
                )

            if rotate3D(legacy_directions.VECTORS[furniture.facing], 3) == longest_dir:
                build_nbt(
                    editor,
                    furniture,
                    palette,
                    Transformation(
                        rotations=3,
                        offset=current,
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
                        rotations=2,
                        offset=current,
                    ),
                    material_params_func=None,
                    build_map=None,
                )
            current = current + subdivision * rotate3D(longest_dir, 1)

        for block in blocks_along_dir_wall:
            filled.add(block)
            for direction in CARDINALS:
                next_block = block + direction
                if next_block not in filled:
                    filled.add(next_block)

        return filled

    while filled is not None and len(placeable.difference(filled)) > 0:
        filled = furnish_along_wall(footprint, filled, stairs_blocks, editor)

    return


def furnish_building(
    cells: list,
    door_coords: ivec3,
    door_dir: ivec3,
    palette: Palette,
    editor: Editor,
    grid: Grid,
    rng: RNG,
):
    num_floors = max(cells, key=lambda x: x[1]).y + 1
    floor_height = 4
    stairs_blocks = set()
    end_corner_type = None

    for floor in range(num_floors):
        filled = set()
        if floor == 0:
            start = door_coords + rotate3D(door_dir, 2) + UP
            filled = set()
            filled.add(start)
            filled.add(start + rotate3D(door_dir, 1))
            filled.add(start + rotate3D(door_dir, 3))
        else:
            stairs_blocks = {
                item for item in stairs_blocks if not isinstance(item, int)
            }
            if end_corner_type == "northeast":
                start = (
                    max(stairs_blocks, key=lambda x: x[0])
                    + SOUTH
                    + ivec3(0, floor_height, 0)
                )
            elif end_corner_type == "southeast":
                start = (
                    max(stairs_blocks, key=lambda x: x[2])
                    + WEST
                    + ivec3(0, floor_height, 0)
                )
            elif end_corner_type == "southwest":
                start = (
                    min(stairs_blocks, key=lambda x: x[0])
                    + NORTH
                    + ivec3(0, floor_height, 0)
                )
            elif end_corner_type == "northwest":
                start = (
                    min(stairs_blocks, key=lambda x: x[2])
                    + EAST
                    + ivec3(0, floor_height, 0)
                )

            filled = {ivec3(x, y + floor_height, z) for (x, y, z) in stairs_blocks}
            filled.add(start)

        cells_with_int_walls = build_interior_walls(
            cells, floor, palette, editor, grid, rng
        )
        if cells_with_int_walls is not None:
            for c, d in cells_with_int_walls:
                c = c + SOUTH
                int_wall_blocks = get_blocks_along_dir_of_cell(c, d, grid)
                filled.update(int_wall_blocks)

        if floor == num_floors - 1:
            has_stairs = False
            end, end_corner_type, floor_space = find_end(
                start, cells, has_stairs, floor, editor, grid, rng, filled, door_dir
            )
            end = end + UP
            path = set()
            path.add(end)
        else:
            has_stairs = True
            end, end_corner_type, floor_space = find_end(
                start, cells, has_stairs, floor, editor, grid, rng, filled, door_dir
            )
            end = end + UP
            path = set()
            path.add(end)
            stairs_blocks, free_for_stairs = build_stairs(
                end, end_corner_type, floor_height, palette, editor
            )
            filled.update(path, stairs_blocks, free_for_stairs)
            filled.add(end)

        furnish(floor_space, filled, stairs_blocks, path, palette, editor, grid, rng)
