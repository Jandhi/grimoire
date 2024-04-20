from gdpc import Block
from maps.map import Map
from terrain.logger import TREE_AND_LEAF_BLOCKS
from gdpc.vector_tools import ivec2, ivec3
from districts.district import District

def district_analyze(district: District, map: Map):
    average = district.average()
    average_height = average.y
    water_blocks = 0
    forest_blocks = 0
    blocks_of_average_height = 0
    number_of_points = len(district.points)

    for point in district.points:
        biome = map.biome_at(ivec2(point.x, point.z))
        block = map.block_at(ivec2(point.x, point.z))
        water = map.water_at(ivec2(point.x, point.z))
        if biome not in district.biome_dict:
            district.biome_dict[biome] = 1
        else:
            district.biome_dict[biome] += 1
        if water:
            water_blocks+=1
        elif block.id in TREE_AND_LEAF_BLOCKS:
            forest_blocks += 1
        if point.y < average_height + 5 and point.y > average_height - 5:
            blocks_of_average_height += 1

    district.roughness = 1 - blocks_of_average_height/number_of_points #change this caluclation to average difference of neighbour block height
    district.water_percentage = water_blocks/number_of_points
    district.forested_percentage = forest_blocks/number_of_points