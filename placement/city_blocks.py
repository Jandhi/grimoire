from districts.district import District
from gdpc import Editor, Block, WorldSlice
from gdpc.vector_tools import ivec2, ivec3
from sets.set_operations import split, calculate_stretch
from sets.find_outer_points import find_outer_and_inner_points

MAXIMUM_SIZE = 2000

UNSPLITTABLE_SIZE = 100 
MAXIMUM_STRETCH_RATIO = 5

EDGE_THICKNESS = 2

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

def add_city_blocks(editor : Editor, districts : list[District], world_slice : WorldSlice):
    candidate_sets = []
    final_sets = []

    for district in districts:
        candidate_sets.append(district.points_2d.copy())

    while len(candidate_sets) > 0:
        candidate_set = candidate_sets.pop(0)

        if block_is_admissible(candidate_set): # set is not good
            final_sets.append(candidate_set)
        else:
            a, b = split(candidate_set)
            candidate_sets.append(a)
            candidate_sets.append(b)

    for final_set in final_sets:
        outer, inner = find_outer_and_inner_points(final_set, EDGE_THICKNESS)

        for point in outer:
            editor.placeBlock(ivec3(point.x, world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][point.x][point.y], point.y), Block('cobblestone'))