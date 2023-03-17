from gdpc import WorldSlice
from districts.district import District
from structures.directions import cardinal, get_ivec2
from gdpc.vector_tools import Rect, ivec2, distance, ivec3, Box

# Tells the districts what neighbours they have and why
def establish_adjacency(world_slice : WorldSlice, districts : list[District], district_map : list[list[District]]):
    build_box = world_slice.box
    rect = Rect((0, 0), (build_box.size.x, build_box.size.z)) # rect of build area, with (0, 0) as corner
    for x in range(build_box.size.x):
        for z in range(build_box.size.z):
            # Don't consider unclaimed territory
            if district_map[x][z] == None:
                continue

            district = district_map[x][z]
            is_edge = False
            height = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z]

            if x == 0 or z == 0: # label edge districts as non-urban
                district.is_urban = False

            for point in (ivec2(x + 1, z), ivec2(x, z + 1)):
                if not rect.contains(point): # out of bounds
                    district.is_urban = False
                    continue

                point_height = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][point.x][point.y]

                if abs(height - point_height) > 1: # impassable, not neighbours
                    continue

                point_district = district_map[point.x][point.y]

                # they are neighbours
                if point_district == district: # same district, uninteresting
                    continue 

                if point_district == None:
                    is_edge = True
                    district.adjacencies_total += 1 # log an empty adjacency
                    continue

                is_edge = True
                district.add_adjacency(point_district)
                point_district.add_adjacency(district)
            
            if is_edge:
                district.edges.add(ivec2(x, z))




