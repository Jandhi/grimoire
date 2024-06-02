# Allows code to be run in root directory
import sys

sys.path[0] = sys.path[0].removesuffix("tests\\placement")

# Actual file
from gdpc import Editor

from grimoire.core.assets.load_assets import load_assets
from grimoire.core.maps import Map
from grimoire.core.noise.rng import RNG
from grimoire.districts.generate_districts import generate_districts
from grimoire.palette import Palette
from grimoire.placement.city_blocks import add_city_blocks
from grimoire.terrain.plateau import plateau
from grimoire.terrain.smooth_edges import smooth_edges

SEED = 0xBABAB00E
DO_TERRAFORMING = False

editor = Editor(buffering=True, caching=True)
load_assets("assets")

area = editor.getBuildArea()
editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
print("World slice loaded!")

world_map = Map(world_slice)
districts, district_map, _, _ = generate_districts(
    SEED, build_rect, world_slice, world_map
)
world_map.districts = district_map

# set up palettes
eligible_palettes = list(
    filter(lambda palette: "desert" in palette.tags, Palette.all())
)
rng = RNG(SEED, "palettes")

for district in districts:
    palettes = [
        Palette.find("dwarven"),
        Palette.find("dwarven"),
        Palette.find("dwarven"),
    ]

    for i in range(3):
        district.palettes.append(rng.pop(palettes))

# plateau stuff
if DO_TERRAFORMING:
    print("starting plateauing")
    for district in districts:
        if not district.is_urban:
            continue

        plateau(district, district_map, world_slice, editor, world_map.water)

    editor.flushBuffer()  # this is needed to reload the world slice properly
    print("Reloading worldSlice")
    world_slice = editor.loadWorldSlice(build_rect)
    world_map.world = world_slice

    smooth_edges(
        build_rect, districts, district_map, world_slice, editor, world_map.water
    )

    editor.flushBuffer()  # this is needed to reload the world slice properly
    print("Reloading worldSlice")
    world_slice = editor.loadWorldSlice(build_rect)
    world_map.world = world_slice
    world_map.correct_district_heights(districts)
# done

# draw_districts(districts, build_rect, district_map, map.water, world_slice, editor)


add_city_blocks(editor, districts, world_map, SEED, is_debug=True)
