from gdpc.vector_tools import ivec3
from districts.tests.place_colors import get_color_differentiated, place_relative_to_ground
from maps.map import Map

def draw_districts(districts, build_rect, district_map, map : Map, super_district_map, editor):
    print('Drawing districts')
    for x in range(build_rect.size.x):
        for z in range(build_rect.size.y):
            district = district_map[x][z]
            super_district = super_district_map[x][z]
            if district is None:
                continue
        
            #elif district not in districts:
            #    district = 

            #block = get_color_differentiated(district, districts, map.water[x][z])

            block = get_colour_type(district.type)
            place_relative_to_ground(x, 0, z, block, map, editor)

            y = map.height_no_tree[x][z]
            if ivec3(x, y, z) in district.edges:
                place_relative_to_ground(x, -1, z, block, map, editor)
                place_relative_to_ground(x, 0, z, 'glass', map, editor)

def get_colour_type(type):
    if type == 'URBAN':
        return 'blue_terracotta'
    elif type == 'RURAL':
        return 'green_terracotta'
    else:
        return 'red_terracotta'
        

def get_colour_roughness(roughness):
    if roughness < 2:
        return 'blue_terracotta'
    elif roughness <4:
        return 'green_terracotta'
    elif roughness <6:
        return 'white_terracotta'
    elif roughness <8:
        return 'yellow_terracotta'
    elif roughness <10:
        return 'orange_terracotta'
    elif roughness <12:
        return 'red_terracotta'
    elif roughness <14:
        return 'black_terracotta'
    
def get_colour_gradient(gradient):
    if gradient < .2:
        return 'blue_terracotta'
    elif gradient < .4:
        return 'green_terracotta'
    elif gradient < .6:
        return 'white_terracotta'
    elif gradient < .8:
        return 'yellow_terracotta'
    elif gradient <1.0:
        return 'orange_terracotta'
    elif gradient <1.2:
        return 'red_terracotta'
    elif gradient <1.4:
        return 'black_terracotta'

colors = [
    'white',
    'orange',
    'magenta', 
    'light_blue', 
    'yellow', 
    'lime', 
    'pink', 
    'gray', 
    'light_gray', 
    'cyan', 
    'purple', 
    'blue', 
    'brown', 
    'green', 
    'red', 
    'black'
]