from gdpc import Block
from maps.map import Map
from terrain.logger import TREE_AND_LEAF_BLOCKS
from gdpc.vector_tools import ivec2, ivec3
from districts.district import District
import math

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
            n1 = map.height_at(ivec2(point.x + 1, point.z))
        except:
            n1 = point.y
        try:
            n2 = map.height_at(ivec2(point.x - 1, point.z))
        except:
            n2 = point.y
        try:
            n3 = map.height_at(ivec2(point.x, point.z + 1))
        except:
            n3 = point.y
        try:
            n4 = map.height_at(ivec2(point.x, point.z - 1))
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
    
    district.border = False #TO DO
