from gdpc import Block
from ..core.maps import Map
from gdpc.vector_tools import ivec2, ivec3
from districts.district import District, SuperDistrict
import math

URBAN_SIZE = 800 #max number of urban districts
BEST_SCORE = 0.65 #score needed to become urban in relation to prime urban district

def district_analyze(district: District, map: Map):
    average = district.average()
    average_height = average.y
    water_blocks = 0
    leaf_blocks = 0
    neighbour_height = 0
    number_of_points = len(district.points)
    district.biome_dict = {}
    district.surface_blocks = {}

    root_mean_square_height = 0

    for point in district.points:
        biome = map.biome_at(ivec2(point.x, point.z))
        block = map.block_at(ivec2(point.x, point.z)).id
        water = map.water_at(ivec2(point.x, point.z))
        leaf_height = map.height_at_include_leaf(ivec2(point.x, point.z))

        root_mean_square_height += pow(point.y - average_height, 2)
        #ugly code to prevent from crashing on getting out of bounds error
        try:
            n1 = map.height_no_tree[point.x][point.z]
        except:
            n1 = point.y
        try:
            n2 = map.height_no_tree[point.x][point.z]
        except:
            n2 = point.y
        try:
            n3 = map.height_no_tree[point.x][point.z]
        except:
            n3 = point.y
        try:
            n4 = map.height_no_tree[point.x][point.z]
        except:
            n4 = point.y
        neighbour_height += (abs(point.y - n1) + abs(point.y - n2) + abs(point.y - n3) + abs(point.y - n4)) / 4

        if biome not in district.biome_dict:
            district.biome_dict[biome] = 1
        else:
            district.biome_dict[biome] += 1
        if block not in district.surface_blocks:
            district.surface_blocks[block] = 1
        else:
            district.surface_blocks[block] += 1
        if water:
            water_blocks+=1
        elif point.y != leaf_height: #discrepancy between height map including leaves and normal height = leaves above block
            leaf_blocks += 1

    district.roughness = math.sqrt(root_mean_square_height/number_of_points) #root mean square
    district.gradient = neighbour_height/number_of_points #average difference of neighbour block height 
    district.water_percentage = water_blocks/number_of_points
    district.forested_percentage = leaf_blocks/number_of_points

def district_classification(districts: list[District]):

    #determine if district unbuildable
    for district in districts:
        if district.is_border:
            district.type = 'OFF-LIMITS'
        elif district.roughness > 6 or district.gradient > 1.0:
            district.type = 'OFF-LIMITS'

    #select prime urban spot
    prime_urban_district = None
    for district in districts:
        if district.type != None or district.water_percentage > 0.33:
            continue
        elif prime_urban_district == None:
            prime_urban_district = district
        else:
            roughness_difference = prime_urban_district.roughness - district.roughness
            gradient_difference = (prime_urban_district.gradient - district.gradient)/3
            forest_difference = prime_urban_district.forested_percentage - district.forested_percentage
            water_difference = prime_urban_district.water_percentage - district.water_percentage
            overall_difference = roughness_difference + gradient_difference + forest_difference + water_difference
            if overall_difference > 0:
                prime_urban_district = district
    prime_urban_district.type = 'URBAN'
   
    # check each district (regardless of adjacency for compatibility to be urban in relation to prime)

    for district in districts:
        if district.type == None:
            score = get_candidate_score_no_adjacency(prime_urban_district, district)
            if score > BEST_SCORE:
                district.type = 'URBAN'
            else:
                continue
        else:
            continue


    #rest is rural
    for district in districts:
        if district.type != None:
            continue

        district.type = 'RURAL'

#assumes the child districts have already been classified
def super_district_classification(districts: list[SuperDistrict]):
    #set deterministic district types
    #select prime urban spot
    prime_urban_district = None
    for district in districts:
        if district.is_border:
            district.type = 'OFF-LIMITS'
        else:
            score = district.get_subtypes_score()
            if score > 1.5:
                district.type = 'OFF-LIMITS'
            elif score > 0.5:
                district.type = 'RURAL'
            elif prime_urban_district == None:
                prime_urban_district = district
            else:
                if score < prime_urban_district.get_subtypes_score():
                    prime_urban_district = district
                elif score == prime_urban_district.get_subtypes_score():
                    roughness_difference = prime_urban_district.roughness - district.roughness
                    gradient_difference = (prime_urban_district.gradient - district.gradient)/3
                    forest_difference = prime_urban_district.forested_percentage - district.forested_percentage
                    water_difference = prime_urban_district.water_percentage - district.water_percentage
                    overall_difference = roughness_difference + gradient_difference + forest_difference + water_difference
                    if overall_difference > 0:
                        prime_urban_district = district

    prime_urban_district.type = 'URBAN'
    urban_districts = [prime_urban_district]
    urban_count = 1
    #expand out city from prime urban districts
    while urban_count < URBAN_SIZE:
        #get options
        option_set = set()
        for district in urban_districts:
            neighbours = district.get_adjacent_districts()
            for neighbour in neighbours:
                if neighbour.type != None:
                    continue
                option_set.add(neighbour)

        #All options alraedy vetted as being urban possible
        best_score = -1 
        best = None

        for district in option_set:
            score = get_candidate_score(prime_urban_district, district)
            if score > best_score:
                best = district
                best_score = score

        if best is None:
            break
        else:
            best.type = 'URBAN'
            urban_districts.append(best)
            urban_count+=1

    #rest is rural
    for district in districts:
        if district.type == None:
            district.type = 'RURAL'


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

def get_candidate_score_no_adjacency(district : District, candidate : District) -> float:
    
    biome_score = 1 - sum(abs(district.biome_dict[key]/district.area - candidate.biome_dict.get(key,0)/candidate.area)
                            for key in district.biome_dict.keys())/len(district.biome_dict.keys())
    
    water_score = 1 - abs(district.water_percentage - candidate.water_percentage)

    forest_score = 1 - abs(district.forested_percentage - candidate.forested_percentage)

    gradient_score = 1 - abs(district.gradient - candidate.gradient)/2

    roughness_score = 1 / (abs(district.roughness - candidate.roughness) + 1)

    return (biome_score + water_score + forest_score + gradient_score + roughness_score)/5