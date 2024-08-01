import math

from gdpc.vector_tools import dropY, rotate2D
from glm import ivec3, ivec2
from gdpc import Editor, Block

from grimoire.core.maps import Map
from grimoire.core.noise.rng import RNG
from grimoire.terrain.set_height import set_height


def build_signpost(editor: Editor, path: list[ivec3], build_map: Map, rng: RNG):
    end_point = dropY(path[0])
    target_point = dropY(path[3] if len(path) > 3 else path[-1])

    diff = target_point - end_point

    offset = normalize_to_length(rotate2D(diff, 1), 2)

    point_a = end_point + offset
    point_b = end_point - offset

    sign_point = None

    if not build_map.is_in_bounds2d(point_a):
        sign_point = point_b
    elif not build_map.is_in_bounds2d(point_b):
        sign_point = point_a
    elif abs(path[0].y - build_map.height_at(point_a)) < abs(
        path[0].y - build_map.height_at(point_b)
    ):
        sign_point = point_a
    elif abs(path[0].y - build_map.height_at(point_a)) > abs(
        path[0].y - build_map.height_at(point_b)
    ):
        sign_point = point_b
    else:
        sign_point = point_a if rng.chance(1, 2) else point_b

    if not sign_point:
        return

    angle = None

    if diff.x == 0:
        if diff.y > 0:
            angle = 4
        else:
            angle = 12
    elif diff.y == 0:
        if diff.x > 0:
            angle = 0
        else:
            angle = 8
    else:
        angle = int((math.atan(diff.y / diff.x)) / (2 * math.pi) * 16)

    if sign_point == point_a:
        data = '{back_text:{color:"black",has_glowing_text:0b,messages:[\'{"text":"that way"}\',\'{"text":"to town"}\',\'{"text":"<---"}\',\'{"text":""}\']},front_text:{color:"black",has_glowing_text:0b,messages:[\'{"text":""}\',\'{"text":""}\',\'{"text":""}\',\'{"text":""}\']},is_waxed:0b}'
    else:
        data = '{back_text:{color:"black",has_glowing_text:0b,messages:[\'{"text":""}\',\'{"text":""}\',\'{"text":""}\',\'{"text":""}\']},front_text:{color:"black",has_glowing_text:0b,messages:[\'{"text":"this way"}\',\'{"text":"to town"}\',\'{"text":"--->"}\',\'{"text":""}\']},is_waxed:0b}'

    set_height(sign_point.x, path[0].y, sign_point.y, build_map.world, editor)

    if (
        editor.getBlock(ivec3(sign_point.x, path[0].y - 1, sign_point.y))
        == "minecraft:sand"
    ):
        editor.placeBlock(
            ivec3(sign_point.x, path[0].y - 1, sign_point.y), Block("sandstone")
        )

    editor.placeBlock(
        ivec3(sign_point.x, path[0].y, sign_point.y),
        Block("oak_sign", states={"rotation": str(angle)}, data=data),
    )


def normalize_to_length(vec: ivec2, desired_length: int):
    current_length = (float(vec.x) ** 2 + float(vec.y) ** 2) ** 0.5
    return ivec2(
        int(vec.x * desired_length / current_length),
        int(vec.y * desired_length / current_length),
    )
