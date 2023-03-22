from gdpc.vector_tools import Rect, ivec2, distance, ivec3
from gdpc import WorldSlice
from structures.directions import cardinal, get_ivec2

#finds the neighbours points of a point in a set
def get_neighbours_in_set(point : ivec2, set : list[ivec2]) -> list[ivec2]:
    neighbours = []
    
    for direction in cardinal:
        delta = get_ivec2(direction)
        neighbour = point + delta

        if neighbour in set:
            neighbours.append(neighbour)

    return neighbours

#returns the subset of points which are edge points, returns both a list and dict
def get_outer_points(points : list[ivec2], world_slice : WorldSlice): # -> list[ivec2], dict:
    outer_points: list[ivec2] = []
    outer_points_dict: dict() = {}

    for point in points:
        if len(get_neighbours_in_set(point, points)) != 4:
            outer_points.append(point)
            outer_points_dict[point] = True
        
    return outer_points, outer_points_dict