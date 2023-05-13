from districts.district import District
from gdpc import Editor, Block, WorldSlice
from gdpc.vector_tools import ivec2, ivec3, distance2
from sets.set_operations import split, calculate_stretch
from sets.find_outer_points import find_outer_and_inner_points
from noise.rng import RNG
from structures.directions import cardinal, get_ivec2
from utils.bounds import is_in_bounds2d

MAXIMUM_SIZE = 2000

UNSPLITTABLE_SIZE = 100 
MAXIMUM_STRETCH_RATIO = 5
EDGE_THICKNESS = 2
DESIRED_BLOCK_SIZE = 500

def block_is_admissible(points : set[ivec2]) -> bool:
    # We will automatically pass this as it should not be split again
    if len(points) <= UNSPLITTABLE_SIZE:
        return True
    
    if len(points) > MAXIMUM_SIZE:
        return False
    
    stretch = calculate_stretch(points)

    if stretch.x / stretch.y > MAXIMUM_STRETCH_RATIO or stretch.y / stretch.x > MAXIMUM_STRETCH_RATIO:
        return False
    
    return True

def generate_bubbles(rng : RNG, districts : list[District], desired_block_size = 1000, minimum_point_distance = 10) -> list[ivec2]:
    points = []

    for district in districts:
        desired_point_amount = district.area // desired_block_size
        district_points_generated = 0
        trials = 0
        max_trials = 2 * desired_point_amount
        district_points = list(district.points_2d)

        while trials < max_trials and district_points_generated < desired_point_amount:
            trials += 1
            point = rng.pop(district_points)

            if any(distance2(point, other) < minimum_point_distance for other in points):
                continue
            
            district_points_generated += 1
            points.append(point)
    
    return points

def bubble_out(bubbles : list[ivec2], district_map : list[list[District]], world_slice : WorldSlice) -> tuple[list[set[ivec2]], list[list[set[ivec2]]]]:
    block_map = [[None for _ in range(len(district_map[0]))] for _ in range(len(district_map))]
    blocks = [set() for bubble in bubbles]

    for i, bubble in enumerate(bubbles):
        blocks[i].add(bubble)
        block_map[bubble.x][bubble.y] = blocks[i]

    queue = [bubble for bubble in bubbles]

    def is_urban(vec : ivec2):
        district = district_map[vec.x][vec.y]
        return district != None and district.is_urban

    while len(queue) > 0:
        point = queue.pop(0)
        block = block_map[point.x][point.y]

        for direction in cardinal:
            neighbour = point + get_ivec2(direction)

            if not is_in_bounds2d(neighbour, world_slice):
                continue

            point_y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][point.x][point.y]
            neighbour_y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][neighbour.x][neighbour.y]

            if abs(point_y - neighbour_y) > 1:
                continue

            if block_map[neighbour.x][neighbour.y] != None:
                continue

            if not is_urban(neighbour):
                continue

            block_map[neighbour.x][neighbour.y] = block
            block.add(neighbour)
            queue.append(neighbour)
    
    return blocks, block_map

def find_directions(block : set[ivec2]) -> dict[ivec2, str]:
    pass

def add_city_blocks(editor : Editor, districts : list[District], district_map : list[list[District]], world_slice : WorldSlice, seed : int):
    rng = RNG(seed, 'add_city_blocks')

    bubbles = generate_bubbles(rng, districts)
    blocks, block_map = bubble_out(bubbles, district_map, world_slice)

    for block in blocks:
        outer, inner = find_outer_and_inner_points(block, EDGE_THICKNESS)

        for point in outer:
            editor.placeBlock(ivec3(point.x, world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][point.x][point.y], point.y), Block('cobblestone'))