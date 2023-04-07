from gdpc import Editor, WorldSlice, Block
from gdpc.vector_tools import ivec3, ivec2
from structures.directions import cardinal, get_ivec2
from utils.bounds import is_in_bounds2d

def build_highway(points : list[ivec3], editor : Editor, world_slice: WorldSlice, water_map : list[list[bool]], building_map : list[list[str]]):
    master_points    : set[ivec2] = set()
    neighbour_points : set[ivec2] = set()
    final_points     : dict[ivec2, int] = {}

    for point in points:
        point_2d = ivec2(point.x, point.z)

        master_points.add(point_2d)
        final_points[point_2d] = point.y

        for direction in cardinal:
            neighbour = point_2d + get_ivec2(direction)

            if not is_in_bounds2d(neighbour, world_slice):
                continue

            if neighbour in neighbour_points or neighbour in master_points:
                continue

            neighbour_points.add(neighbour)
            final_points[neighbour] = point.y # this is an estimate of height to help the next step
    
    if False:
        # We calculate the neighbours of the original highway to be the average height of its neighbours
        for point in neighbour_points:
            total_y = 0
            total_count = 0
            
            for direction in cardinal:
                neighbour = point + get_ivec2(direction)

                if neighbour not in final_points:
                    continue
                
                total_y += final_points[neighbour]
                total_count += 1

            average = (total_y + (total_count - 1)) // total_count # formula rounds up, since we would rather have the block "higher" as a slab
            final_points[point] = average

    for point in final_points:
        x, z = point
        y = final_points[point] - 1

        editor.placeBlock((x, y, z), Block('cobblestone'))

        if world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z] > y:
            editor.placeBlock((x, y + 1, z), Block('air'))
            editor.placeBlock((x, y + 2, z), Block('air'))
            editor.placeBlock((x, y + 3, z), Block('air'))