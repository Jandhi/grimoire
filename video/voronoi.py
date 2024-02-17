# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\video')

from districts.tests.draw_districts import draw_districts
from districts.tests.place_colors import get_color_differentiated, place_relative_to_ground
from structures.directions import cardinal, vector
from terrain.logger import log_trees

from districts.generate_districts import spawn_districts
from maps.build_map import get_build_map
from maps.water_map import get_water_map

from gdpc import Editor, Block, WorldSlice
from gdpc.vector_tools import ivec2, ivec3
from districts.district import District

editor = Editor(buffering=True, caching=True)
area = editor.getBuildArea()
print(area)
editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

log_trees(editor, build_rect, world_slice)

print("Reload post logging slice!")
world_slice = editor.loadWorldSlice(build_rect)

seed = 13


water_map = get_water_map(world_slice)
build_map = get_build_map(world_slice)

districts = spawn_districts(seed, build_rect, world_slice)
district_map : list[list[District]] = [[None for _ in range(build_rect.size.y)] for _ in range(build_rect.size.x)]

for district in districts:
    origin = district.origin
    district_map[origin.x][origin.z] = district

queue = [district.origin for district in districts]
visited = set([tuple(district.origin) for district in districts])

def add_point_to_district(point : ivec3, district : District):
    district_map[point.x][point.z] = district
    district.add_point(point)

def get_neighbours(point: ivec3, world_slice: WorldSlice) -> list[ivec3]:
    neighbours = []
    height_map = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']

    for direction in cardinal:
        delta = vector(direction)
        neighbour = point + delta


        if neighbour.x < 0 or neighbour.z < 0 or neighbour.x >= len(height_map) or neighbour.z >= len(height_map[0]):
            # out of bounds
            continue

        neighbour.y = height_map[neighbour.x][neighbour.z]
        neighbours.append(neighbour)
    return neighbours

# first pass normal queue
while len(queue) > 0:
    point = queue.pop(0)
    district = district_map[point.x][point.z]

    for neighbour in get_neighbours(point, world_slice):
        if tuple(neighbour) in visited:
            continue

        if neighbour.x < 0 or neighbour.x >= build_rect.size.x or neighbour.z < 0 or neighbour.z >= build_rect.size.y:
            continue

        visited.add(tuple(neighbour))
        add_point_to_district(neighbour, district)

        queue.append(neighbour)
        continue

print(sum(district.points.__len__() for district in districts))

for district in districts:
    for point in district.points:
        x, z = point.x, point.z

        block = get_color_differentiated(district, districts, water_map[x][z])

        y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z]
        place_relative_to_ground(x, 0, z, block, world_slice, editor)
