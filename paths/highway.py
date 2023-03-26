from gdpc.vector_tools import ivec3, distance
from gdpc import WorldSlice
from structures.directions import cardinal, get_ivec3

def create_highway(start : ivec3, end : ivec3, world_slice : WorldSlice, water_map : list[list[bool]]):


    def get_cost(prev_cost : int, path : list[ivec3]):
        prev_heuristic = distance(path[-2], end)

        path_cost = prev_cost - prev_heuristic
        base_length_cost = 2 # added as length of path increases

        return path_cost + base_length_cost + distance(path[-2], path[-1]) + distance(path[-1], end)
    
    # prefer 4 out neighbours, but will accept 2 out
    def get_neighbours(point : ivec3):
        neighbours = []
        
        for direction in cardinal:
            direction_vector = get_ivec3(direction)

            # First consider 4 out
            neighbour = point + direction_vector * 4
            neighbour.y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][neighbour.x][neighbour.z]

            if abs(point.y - neighbour.y) <= 2:
                neighbours.append(neighbour)
                continue

            # Then consider 2 out
            neighbour = point + direction_vector * 2
            neighbour.y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][neighbour.x][neighbour.z]

            if abs(point.y - neighbour.y) <= 2:
                neighbours.append(neighbour)
                continue