# Allows code to be run in root directory
import sys

sys.path[0] = sys.path[0].removesuffix("tests\\districts")


from gdpc import Block, Editor

# Actual file
from grimoire.core.maps import Map, get_water_map
from grimoire.districts.generate_districts import generate_districts
from tests.districts.draw_districts import draw_districts

SEED = 752

editor = Editor(buffering=True, caching=True)

area = editor.getBuildArea()
editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

world_map = Map(world_slice)
districts, district_map, _, super_districts = generate_districts(
    SEED, build_rect, world_slice, world_map
)

draw_districts(districts, build_rect, district_map, world_map, super_districts, editor)

for district in districts:
    x = district.origin.x
    z = district.origin.z

    y = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][x][z] + 10
    editor.placeBlock((x, y, z), Block("sea_lantern"))
