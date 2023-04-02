from gdpc.vector_tools import ivec3, distance
from gdpc import WorldSlice, Editor
from structures.directions import all_8, get_ivec3
from paths.a_star import a_star
from utils.bounds import is_in_bounds

HEURISTIC_WEIGHT = 3

def route_highway(start : ivec3, end : ivec3, world_slice : WorldSlice, water_map : list[list[bool]], editor : Editor) -> list[ivec3]:
    
    def get_cost(prev_cost : int, path : list[ivec3]):
        if len(path) == 1:
            return 2 * distance(path[-1], end)

        prev_heuristic = HEURISTIC_WEIGHT * distance(path[-2], end)

        path_cost = prev_cost - prev_heuristic
        base_length_cost = 2 # added as length of path increases

        y_diff_penalty = abs(path[-1].y - path[-2].y) * 2

        return path_cost + base_length_cost + y_diff_penalty + distance(path[-2], path[-1]) + HEURISTIC_WEIGHT * distance(path[-1], end)
    
    # prefer 4 out neighbours, but will accept 2 out
    def get_neighbours(point : ivec3):
        neighbours = []
        
        for direction in all_8:
            direction_vector = get_ivec3(direction)

            # First consider 4 out
            neighbour = point + direction_vector * 4

            if is_in_bounds(neighbour, world_slice):
                neighbour.y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][neighbour.x][neighbour.z]

                if abs(point.y - neighbour.y) <= 2 and not water_map[neighbour.x][neighbour.z]:
                    neighbours.append(neighbour)
                    continue


            # Don't consider compounds for short jumps
            if sum(direction_vector) >= 2:
                continue

            # Then consider 2 out
            neighbour = point + direction_vector * 2

            if is_in_bounds(neighbour, world_slice):
                neighbour.y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][neighbour.x][neighbour.z]

                if abs(point.y - neighbour.y) <= 2 and not water_map[neighbour.x][neighbour.z]:
                    neighbours.append(neighbour)
                    continue
                
        return neighbours
    
    return a_star(start, end, get_neighbours, get_cost)