from gdpc import Editor, Block
from gdpc.vector_tools import addY, dropY, ivec3, UP, DOWN, NORTH, SOUTH, EAST, WEST
from glm import ivec2

from grimoire.core.maps import Map
from grimoire.core.noise.rng import RNG
from grimoire.core.styling.blockform import BlockForm
from grimoire.core.structures import legacy_directions
from grimoire.core.structures.legacy_directions import VECTORS
from grimoire.core.styling.materials.material import MaterialParameters
from grimoire.core.styling.palette import BuildStyle, MaterialRole, Palette
from grimoire.districts.gate import Gate
from grimoire.paths.build_highway import build_highway
from grimoire.paths.route_highway import route_highway, fill_out_highway
from grimoire.paths.signposts import build_signpost


def add_gate_path(
    gate: Gate, main_map: Map, editor: Editor, rng: RNG, style: BuildStyle
):
    path_origin = gate.location + VECTORS[gate.direction]

    size = main_map.world.rect.size

    path_end: ivec2 = None
    gate_opposite: ivec3 = None
    perpendicular_directions = None
    if gate.direction == legacy_directions.SOUTH:
        path_end = ivec2(gate.location.x, 0)
        gate_opposite = NORTH
        perpendicular_directions = [WEST, EAST]
    if gate.direction == legacy_directions.NORTH:
        path_end = ivec2(gate.location.x, size.y - 1)
        gate_opposite = SOUTH
        perpendicular_directions = [WEST, EAST]
    if gate.direction == legacy_directions.WEST:
        path_end = ivec2(size.x - 1, gate.location.z)
        gate_opposite = EAST
        perpendicular_directions = [NORTH, SOUTH]
    if gate.direction == legacy_directions.EAST:
        path_end = ivec2(0, gate.location.z)
        gate_opposite = WEST
        perpendicular_directions = [NORTH, SOUTH]

    def round_to_four(vec: ivec2) -> ivec2:
        return ivec2(vec.x - vec.x % 4, vec.y - vec.y % 4)

    point_a = addY(round_to_four(dropY(path_origin)), gate.location.y)
    point_b = main_map.make_3d(round_to_four(path_end))

    # don't do it in water
    if main_map.water_at(dropY(point_b)):
        return

    highway = route_highway(point_a, point_b, main_map, editor, is_debug=False)
    if highway:
        highway = fill_out_highway(highway)
        build_highway(highway, editor, main_map.world, main_map, style)
        build_signpost(editor, highway, main_map, rng)

        lampposts = []
        radius = 12

        district = main_map.super_districts[highway[0].x][highway[0].y]
        palette: Palette = (
            rng.choose(district.palettes)
            if district and district.palettes
            else Palette.find("japanese_dark_blackstone")
        )
        fence = palette.find_block_id(
            BlockForm.FENCE,
            MaterialParameters(highway[0], 0, 0, 0, None),
            MaterialRole.PRIMARY_WOOD,
        )
        road = Block("sandstone") if style == BuildStyle.DESERT else Block("cobblestone")

        for point in highway:
            nearby_lampposts = False
            for lamppost in lampposts:
                if not nearby_lampposts and (abs(point.x - lamppost[0].x)**2 + abs(point.z - lamppost[0].z)**2) < radius**2:
                    nearby_lampposts = True
            if not nearby_lampposts:
                for offset in perpendicular_directions:
                    if editor.getBlock(point + offset * 2 + DOWN) != road and editor.getBlock(point + offset * 2).id != "oak_sign":
                        lampposts.append([point, offset])
                        break

        for lamppost in lampposts:
            path_origin, offset = lamppost
            editor.placeBlock(path_origin + offset * 2 + DOWN, road)
            editor.placeBlock(path_origin + offset * 2, Block(id=fence))
            editor.placeBlock(path_origin + offset * 2 + UP, Block(id=fence))
            editor.placeBlock(path_origin + offset * 2 + UP * 2, Block(id=fence))
            editor.placeBlock(path_origin + offset * 2 + UP * 3, Block(id=fence))
            editor.placeBlock(path_origin + offset * 2 + UP * 4, Block(id=fence))
            editor.placeBlock(path_origin + offset + UP * 4, Block(id=fence))
            editor.placeBlock(path_origin + offset + UP * 3, Block(id="lantern", states={"hanging": "true"}))