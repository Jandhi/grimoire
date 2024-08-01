# Allows code to be run in root directory
import itertools
import sys
import time
from pathlib import Path

from gdpc.world_slice import WorldSlice

sys.path[0] = sys.path[0].removesuffix(str(Path("tests/placement")))
print(f"PATH: {sys.path[0]}")

from gdpc import Box, Editor
from gdpc.lookup import DIRTS, GRANULARS

# Actual file
from gdpc.vector_tools import ivec3
from glm import ivec2

from grimoire.core.assets.asset_loader import load_assets
from grimoire.core.maps import Map, get_build_map
from grimoire.core.noise.rng import RNG
from grimoire.core.styling.biome_lookup import get_style_and_palettes
from grimoire.core.utils.geometry import get_surrounding_points
from grimoire.core.utils.misc import growth_spurt, kill_items
from grimoire.core.utils.sets.find_outer_points import find_outer_and_inner_points
from grimoire.districts.district import DistrictType
from grimoire.districts.district_analyze import (
    district_analyze,
    district_classification,
    super_district_classification,
)
from grimoire.districts.district_painter import plant_forest, replace_ground
from grimoire.districts.generate_districts import generate_districts
from grimoire.districts.paint_palette import PaintPalette
from grimoire.districts.wall import (
    build_wall_standard_with_inner,
    get_wall_points,
    order_wall_points,
)
from grimoire.paths.gate_paths import add_gate_path
from grimoire.placement.city_blocks import add_city_blocks
from grimoire.terrain.forest import Forest
from grimoire.terrain.plateau import plateau
from grimoire.terrain.smooth_edges import smooth_edges
from grimoire.terrain.tree_cutter import log_trees

SEED = 0x4473
DO_TERRAFORMING = True  # Set this to true for the final iteration
LOG_TREES = True
DO_WALL = True
DO_RURAL = True  # Not worth it
DO_URBAN = True
RESET_AFTER_TEST = False  # FIXME: Restoration crashes

BUFFER_LIMIT = 32
SLEEP_DELAY = 1

load_assets(str(Path("grimoire/asset_data")))

# ==== EDITOR and WORLD settings ====
editor = Editor(buffering=True, bufferLimit=BUFFER_LIMIT, caching=True)

editor.runCommand("gamerule doFireTick false")

area = editor.getBuildArea()

# can't to do areas too large yet
if area.size.x > 1000:
    x = area.center.x - 400
    z = area.center.z - 400
    editor.setBuildArea(Box((x, 0, z), (350, area.size.y, 350)))

area = editor.getBuildArea()

editor.transform = (area.begin.x, 0, area.begin.z)

print("Loading world slice...")
build_rect = area.toRect()

if RESET_AFTER_TEST:
    editor.caching = True
    editor.cacheLimit = 0
    backup_slice: WorldSlice = editor.loadWorldSlice(build_rect, cache=True)

world_slice: WorldSlice = editor.loadWorldSlice(build_rect)

print("World slice loaded!")

main_map = Map(world_slice)
districts, district_map, super_districts, super_district_map = generate_districts(
    SEED, build_rect, world_slice, main_map
)
main_map.districts = district_map
main_map.super_districts = super_district_map

for district in super_districts:
    district_analyze(district, main_map)

district_classification(districts)
super_district_classification(super_districts)

inner_points = []

for x in range(build_rect.size.x):
    for z in range(build_rect.size.y):
        super_district = super_district_map[x][z]

        if super_district is None:
            continue
        elif super_district.type == DistrictType.URBAN:
            inner_points.append(ivec2(x, z))

if LOG_TREES:  # TO DO, only log urban
    logged_points = inner_points + list(get_surrounding_points(set(inner_points), 5))
    log_trees(editor, logged_points, world_slice)

editor.flushBuffer()  # this is needed to reload the world slice properly
print("Reloading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
main_map.world = world_slice
print("World slice reloaded!")

# plateau stuff
if DO_TERRAFORMING:  # think about terraforming deal with districts/superdistricts
    print("starting plateauing")
    for super_district in super_districts:
        if super_district.type != DistrictType.URBAN:
            continue

        plateau(super_district, super_district_map, world_slice, editor, main_map.water)

    editor.flushBuffer()  # this is needed to reload the world slice properly
    print("Reloading worldSlice")
    world_slice = editor.loadWorldSlice(build_rect)
    main_map.world = world_slice

    smooth_edges(
        build_rect,
        super_districts,
        super_district_map,
        world_slice,
        editor,
        main_map.water,
    )

    editor.flushBuffer()  # this is needed to reload the world slice properly
    print("Reloading worldSlice")
    world_slice = editor.loadWorldSlice(build_rect)
    main_map.world = world_slice
    main_map.correct_district_heights(districts)
# done

print("sleepy time to reduce http traffic")
time.sleep(SLEEP_DELAY)  # to try to reduce http traffic, we'll do a little sleepy time

biomes = {}
for district in super_districts:
    for biome in district.biome_dict:
        if biome not in biomes:
            biomes[biome] = 0

        biomes[biome] += district.biome_dict[biome]

most_prevalent_biome = max(biomes.items(), key=lambda kp: kp[1])[0]

print(f"MOST PREVALENT BIOME IS {most_prevalent_biome}")

style, eligible_palettes = get_style_and_palettes(most_prevalent_biome)
rng = RNG(SEED, "palettes")

for district in super_districts:
    palettes = eligible_palettes.copy()

    for _ in range(min(3, len(eligible_palettes))):
        district.palettes.append(rng.pop(palettes))

rng = RNG(SEED)
palette = rng.choose(eligible_palettes)

build_map = get_build_map(world_slice, 20)


# draw_districts(districts, build_rect, district_map, map.water, world_slice, editor)

# for districts in districts:
#     x = districts.origin.x
#     z = districts.origin.z

#     y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x][z] + 10
#     editor.placeBlock((x, y, z), Block('sea_lantern'))

if DO_URBAN:

    blocks, inners, outers = add_city_blocks(
        editor,
        super_districts,
        main_map,
        SEED,
        style=style,
        is_debug=False,
    )

growth_spurt(editor)

editor.flushBuffer()  # this is needed to reload the world slice properly
print("Reloading world slice...")
build_rect = area.toRect()
world_slice = editor.loadWorldSlice(build_rect)
main_map.world = world_slice
print("World slice reloaded!")

editor.runCommand("gamerule randomTickSpeed 0")

if DO_RURAL:
    permit_blocks = DIRTS

    farmland: PaintPalette = PaintPalette.find("farmland")
    forests = Forest.all()
    crops = list(filter(lambda palette: "crops" in palette.tags, PaintPalette.all()))
    rural_road: PaintPalette = PaintPalette.find("rural_road")

    options = forests + crops

    for super_district in super_districts:
        if super_district.type == DistrictType.RURAL:
            # FIXME: Undefined words "mountainous" etc.
            super_district.roughness > 6 or super_district.gradient > 1.0
            if super_district.forested_percentage > 0.2:
                choice_list = rng.choose([forests, [None]])
            elif (
                super_district.roughness < 3
                and super_district.gradient < 0.5
                and super_district.water_percentage < 0.5
            ):  # NOTE: Unsure how often this will actually occur and not be urban
                choice_list = rng.choose([crops])
            else:
                choice_list = rng.choose([[None]])
            choice = rng.choose(choice_list)

            if isinstance(choice, Forest):  # forest
                outer_district_points, inner_district_points = (
                    find_outer_and_inner_points(super_district.points_2d, 4)
                )
                log_trees(editor, super_district.points_2d, world_slice)
                plant_forest(
                    list(inner_district_points),
                    choice,
                    rng,
                    main_map.water,
                    build_map,
                    editor,
                    world_slice,
                    permit_blocks,
                )
            elif isinstance(choice, PaintPalette):  # crops
                log_trees(editor, super_district.points_2d, world_slice)

                editor.flushBuffer()  # this is needed to reload the world slice properly
                print("Reloading world slice...")
                build_rect = area.toRect()
                world_slice = editor.loadWorldSlice(build_rect)
                main_map.world = world_slice
                print("World slice reloaded!")

                plateau(
                    super_district,
                    super_district_map,
                    world_slice,
                    editor,
                    main_map.water,
                )

                editor.flushBuffer()  # this is needed to reload the world slice properly
                print("Reloading world slice...")
                build_rect = area.toRect()
                world_slice = editor.loadWorldSlice(build_rect)
                main_map.world = world_slice
                print("World slice reloaded!")

                for district in super_district.districts:
                    outer_district_points, inner_district_points = (
                        find_outer_and_inner_points(district.points_2d, 0)
                    )
                    replace_ground(
                        list(inner_district_points),
                        farmland.palette,
                        rng,
                        main_map.water,
                        build_map,
                        editor,
                        world_slice,
                        0,
                        permit_blocks,
                    )
                    replace_ground(
                        list(inner_district_points),
                        choice.palette,
                        rng,
                        main_map.water,
                        build_map,
                        editor,
                        world_slice,
                        1,
                    )
                    replace_ground(
                        list(outer_district_points),
                        rural_road.palette,
                        rng,
                        main_map.water,
                        build_map,
                        editor,
                        world_slice,
                    )
            else:
                continue

            time.sleep(
                SLEEP_DELAY
            )  # to try to reduce http traffic, we'll do a little sleepy time

# WALL

# uncomment one of these to story one of the three wall types

if DO_WALL:
    wall_points, wall_dict = get_wall_points(inner_points, world_slice)
    wall_points_list = order_wall_points(wall_points, wall_dict)

    for wall_points in wall_points_list:
        gates = build_wall_standard_with_inner(
            wall_points,
            wall_dict,
            inner_points,
            editor,
            world_slice,
            main_map.water,
            rng,
            palette,
        )

        for gate in gates:
            add_gate_path(gate, main_map, editor, rng, style)


# build_wall_palisade(wall_points, editor, map.world, map.water, rng, palette)
# build_wall_standard(wall_points, wall_dict, inner_points, editor, map.world, map.water, palette)

# ==== CLEANUP ====

kill_items(editor)
growth_spurt(editor)

if RESET_AFTER_TEST:
    input("Press <enter> to reset the map...")
    editor.buffering = True
    editor.bufferLimit = 4028
    dx, dy, dz = (
        backup_slice.box.size.x,
        backup_slice.box.size.y,
        backup_slice.box.size.z,
    )

    # TODO: Replace with `for v in backup_slice.box`
    total = backup_slice.box.volume
    for current, (x, y, z) in enumerate(
        itertools.product(range(dx), range(dy), range(dz)), start=1
    ):
        print(
            f"{current/total:8.2%}\tResetting {(x, y, z)}... ({current}/{total})",
            end="\r",
        )

        if editor.worldSliceDecay[x][y][z]:
            v = ivec3(x, y, z)
            editor.placeBlock(v, backup_slice.getBlock(v))
    print("Done!")
