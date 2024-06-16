from gdpc import Editor
from gdpc.vector_tools import addY, dropY
from glm import ivec2

from grimoire.core.maps import Map
from grimoire.core.noise.rng import RNG
from grimoire.core.structures import legacy_directions
from grimoire.core.structures.legacy_directions import VECTORS
from grimoire.core.styling.palette import BuildStyle
from grimoire.districts.gate import Gate
from grimoire.paths.build_highway import build_highway
from grimoire.paths.route_highway import route_highway, fill_out_highway
from grimoire.paths.signposts import build_signpost


def add_gate_path(gate: Gate, main_map: Map, editor: Editor, rng: RNG, style : BuildStyle):
    path_origin = gate.location + VECTORS[gate.direction]

    size = main_map.world.rect.size

    path_end: ivec2 = None
    if gate.direction == legacy_directions.SOUTH:
        path_end = ivec2(gate.location.x, 0)
    if gate.direction == legacy_directions.NORTH:
        path_end = ivec2(gate.location.x, size.y - 1)
    if gate.direction == legacy_directions.WEST:
        path_end = ivec2(size.x - 1, gate.location.z)
    if gate.direction == legacy_directions.EAST:
        path_end = ivec2(0, gate.location.z)

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
