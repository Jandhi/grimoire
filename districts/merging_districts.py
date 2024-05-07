from districts.district import District
from districts.district_analyze import district_analyze
from maps.map import Map

RURAL_SIZE_RATIO = 3 # NOTE: not currently used, we expect rural districts to be this times larger in area than urban ones

# Merges districts until we have a target number reached
def merge_down(districts : list[District], district_map : list[list[District]], target_number : int, map: Map):

    identities = {district : district for district in districts} # tracks whether a district is truly itself
    district_count = len(districts)

    ignore = set()

    while district_count > target_number:

        child = find_smallest_adjusted_district(districts, ignore)

        if child == None:
            break

        neighbours : list[District] = child.get_adjacent_districts()

        parent = get_best_merge_candidate(child, neighbours)

        if parent == None:
            ignore.add(child)

            if child.area < 10: # remove garbage district
                districts.remove(child)
                district_count -= 1
                identities[child] = None

            continue

        merge(parent, child, districts, identities)
        district_analyze(parent, map) # NOTE: could optimize by moving the calcucations in merge and using the district numbers instead of recalculating
        district_count -= 1

    fix_map_and_edges(district_map, districts, identities)

def find_smallest_adjusted_district(districts : list[District], ignore : set[District]) -> District:
    smallest = None
    area = 10000000

    for district in districts:
        if district in ignore:
            continue

        if district.area < area:
            smallest = district
            area = district.area

    return smallest 

def get_best_merge_candidate(district : District, options : list[District]) -> District:
    best = None
    best_score = 0.33 #NOTE: minimum score to beat else it won't be merged with any neighbour, to test this value
    candidate_scores = {}

    for option in options:
        if district.is_urban != option.is_urban: # don't merge different types of districts!
            continue

        score = get_candidate_score(district, option)
        candidate_scores[option] = score
        if score > best_score:
            best = option
            best_score = score

    output = f'\tConsidering options for {district}: '
    for candidate, score in candidate_scores.items():
        output += f'({candidate}: {score}) '
    print(output)

    return best 

def get_candidate_score(district : District, candidate : District) -> float:
    #NOTE: option to add some hard limits to scores, where below a certain score in a category it is flat out rejected

    adjacency_score = 1000.0 * district.get_adjacency_ratio(candidate)  / float(candidate.area) 
    
    biome_score = 1 - sum(abs(district.biome_dict[key]/district.area - candidate.biome_dict.get(key,0)/candidate.area)
                            for key in district.biome_dict.keys())/len(district.biome_dict.keys())
    
    water_score = 1 - abs(district.water_percentage - candidate.water_percentage)

    forest_score = 1 - abs(district.forested_percentage - candidate.forested_percentage)

    gradient_score = 1 - abs(district.gradient - candidate.gradient)/2

    roughness_score = 1 / (abs(district.roughness - candidate.roughness) + 1)

    return (adjacency_score * 3 + biome_score + water_score + forest_score + gradient_score + roughness_score)/8

# NOTE: Not currently used
def get_adjusted_area(district :  District) -> int:
    if district.is_urban:
        return district.area
    else:
        return district.area // RURAL_SIZE_RATIO

# merges child district into parent
# NOTE: this will create outdated edges (between parent and child). 
# Edges should be scanned for again after the merging process.
def merge(parent : District, child : District, districts : list[District], identities : dict[District, District]):
    print(f'\tMerging {child} into {parent}')

    districts.remove(child)
    identities[child] = parent

    parent.area  += child.area
    parent.edges |= child.edges # set addition

    parent.points |= child.points
    parent.points_2d |= child.points_2d

    # merge child's neighborus to parent
    for district, adjacency_count in child.adjacency.items():
        if district == parent:
            continue

        if district not in parent.adjacency:
            parent.adjacency[district] = 0

        parent.adjacency[district] += adjacency_count
        parent.adjacencies_total   += adjacency_count

    parent.adjacency.pop(child)

    # switch child for parent in other districts
    for district in districts:
        if district == parent:
            continue

        if child in district.adjacency:
            if parent not in district.adjacency:
                district.adjacency[parent] = 0

            district.adjacency[parent] += district.adjacency[child]
            district.adjacency.pop(child)

    # add alias tracking for district map
    for alias in list(identities.keys()):
        if identities[alias] == child:
            identities[alias] = parent

def fix_map_and_edges(district_map : list[list[District]], districts : list[District], identities : dict[District, District]):
    # Fixes map
    for x in range(len(district_map)):
        for z in range(len(district_map[0])):
            district = district_map[x][z]

            if district != None:
                district_map[x][z] = identities[district]