from heapq import heapify, heappop, heappush

# get_neighbours takes state
# get_cost takes prev_cost and path

def a_star(start, end, get_neighbours, get_cost) -> list:
    first_path = ([start], 0)
    paths = [first_path]

    while len(paths) > 0:
        curr_path, curr_cost = heappop(paths)

        