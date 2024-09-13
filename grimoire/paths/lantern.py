from gdpc import Editor, Block
from gdpc.vector_tools import distance, CARDINALS_2D, NORTH, UP, addY
from glm import ivec2

from grimoire.core.maps import Map, DevelopmentType
from grimoire.core.noise.rng import RNG
from grimoire.core.styling.blockform import BlockForm
from grimoire.core.styling.materials.material import MaterialParameters
from grimoire.core.styling.palette import Palette, MaterialRole
from grimoire.core.utils.sets.set_operations import find_outline

MIN_DIST = 10


def place_lanterns(editor: Editor, city_road: set[ivec2], build_map: Map, rng: RNG):
    outline = find_outline(city_road)

    lanterns = set()

    for point in outline:
        development = build_map.buildings[point.x][point.y]
        if (
            development == DevelopmentType.BUILDING
            or development == DevelopmentType.CITY_WALL
            or build_map.water_at(point)
        ):
            continue

        if any(distance(lantern, point) < MIN_DIST for lantern in lanterns):
            continue

        lanterns.add(point)

    for point in lanterns:
        district = build_map.super_districts[point.x][point.y]
        palette: Palette = (
            rng.choose(district.palettes)
            if district and district.palettes
            else Palette.get("japanese_dark_blackstone")
        )

        road_direction = None

        for direction in CARDINALS_2D:
            if (
                build_map.buildings[point.x + direction.x][point.y + direction.y]
                == DevelopmentType.CITY_ROAD
            ):
                road_direction = direction
                break

        if not road_direction:
            road_direction = rng.choose(list(CARDINALS_2D))

        root = build_map.make_3d(point)

        wall = palette.find_block_id(
            BlockForm.WALL,
            MaterialParameters(root, 0, 0, 0, None),
            MaterialRole.PRIMARY_STONE,
        )

        fence = palette.find_block_id(
            BlockForm.FENCE,
            MaterialParameters(root, 0, 0, 0, None),
            MaterialRole.PRIMARY_WOOD,
        )

        editor.placeBlock(root, Block(id=wall))
        editor.placeBlock(root + UP, Block(id=fence))
        editor.placeBlock(root + 2 * UP, Block(id=fence))
        editor.placeBlock(root + 3 * UP, Block(id=fence))
        editor.placeBlock(root + 3 * UP + addY(road_direction, 0), Block(id=fence))
        editor.placeBlock(
            root + 2 * UP + addY(road_direction, 0),
            Block(id="lantern", states={"hanging": "true"}),
        )
