import itertools

from gdpc.vector_tools import Rect, ivec3

from grimoire.core.maps import Map
from grimoire.districts.district import District, DistrictType, SuperDistrict

from .place_colors import get_color_differentiated, place_relative_to_ground


def draw_districts(
    districts: list[District],  # FIXME: Unused
    build_rect: Rect,
    district_map: list[list[District]],
    main_map: Map,
    super_district_map: list[list[SuperDistrict]],
    editor,
) -> None:
    print("Drawing districts")
    for x, z in itertools.product(range(build_rect.size.x), range(build_rect.size.y)):
        district: District = district_map[x][z]
        super_district: SuperDistrict = super_district_map[x][z]  # FIXME: Unused

        if district is None:
            continue

        # block = get_color_differentiated(district, districts, map.water[x][z])

        block: str = get_colour_type(district.type)
        place_relative_to_ground(x, 0, z, block, main_map, editor)

        y: int = main_map.height_no_tree[x][z]
        if ivec3(x, y, z) in district.edges:
            place_relative_to_ground(x, -1, z, block, main_map, editor)
            place_relative_to_ground(x, 0, z, "glass", main_map, editor)


def get_colour_type(type: DistrictType) -> str:
    if type == DistrictType.URBAN:
        return "blue_terracotta"
    elif type == DistrictType.RURAL:
        return "green_terracotta"
    elif type == DistrictType.OFF_LIMITS:
        return "red_terracotta"
    else:
        return "structure_block"


def get_colour_roughness(roughness: float) -> str:
    if roughness < 2:
        return "blue_terracotta"
    elif roughness < 4:
        return "green_terracotta"
    elif roughness < 6:
        return "white_terracotta"
    elif roughness < 8:
        return "yellow_terracotta"
    elif roughness < 10:
        return "orange_terracotta"
    elif roughness < 12:
        return "red_terracotta"
    elif roughness < 14:
        return "black_terracotta"
    else:
        return "structure_block"


def get_colour_gradient(gradient) -> str:
    if gradient < 0.2:
        return "blue_terracotta"
    elif gradient < 0.4:
        return "green_terracotta"
    elif gradient < 0.6:
        return "white_terracotta"
    elif gradient < 0.8:
        return "yellow_terracotta"
    elif gradient < 1.0:
        return "orange_terracotta"
    elif gradient < 1.2:
        return "red_terracotta"
    elif gradient < 1.4:
        return "black_terracotta"
    else:
        return "structure_block"
