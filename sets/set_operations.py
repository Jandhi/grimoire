from gdpc.vector_tools import ivec2, distance2
from math import atan, pi

def midpoint(points : set[ivec2]) -> ivec2:
    return sum(points) / len(points)

def calculate_stretch(points : set[ivec2]) -> ivec2:
    stretch = ivec2(1, 1)
    mid = midpoint(points)

    for point in points:
        stretch += abs(mid - point)

    return stretch

def voronoi_split(points : set[ivec2], point_a : ivec2, point_b : ivec2) -> tuple[set[ivec2], set[ivec2]]:
    set_a = set()
    set_b = set()

    for point in points:
        if distance2(point, point_a) < distance2(point, point_b):
            set_a.add(point)
        else:
            set_b.add(point)

    return set_a, set_b

def split(points : set[ivec2]) -> tuple[set[ivec2], set[ivec2]]:
    mid = midpoint(points)
    
    best_split = None

    # You want this low like golf
    def split_score(split):
        evenness = abs(len(split[0]) - len(split[1]))

        # maybe add stretch as goal
        stretch_a = calculate_stretch(split[0])
        stretch_b = calculate_stretch(split[1])

        stretch_penalty_a = max(stretch_a.x, stretch_a.y) / min(stretch_a.x, stretch_a.y) 
        stretch_penalty_b = max(stretch_b.x, stretch_b.y) / min(stretch_b.x, stretch_b.y)

        return evenness + stretch_penalty_a * 0.1 + stretch_penalty_b * 0.1 


    for point_a, point_b in [
        (ivec2(1, 0), ivec2(-1, 0)), 
        (ivec2(0, 1), ivec2(0, -1)),
    ]:
        split = voronoi_split(points, mid + point_a, mid + point_b)

        if best_split == None:
            best_split = split
            continue

        if split_score(split) < split_score(best_split):
            best_split = split

    return best_split
