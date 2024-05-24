import contextlib
import math
from typing import Type

from gdpc import Block
from gdpc.vector_tools import ivec2, ivec3

from ..core.maps import Map
from ..districts.district import District, DistrictType, SuperDistrict

URBAN_SIZE = 800  # max number of urban districts
BEST_SCORE = 0.6  # score needed to become urban in relation to prime urban district


def district_analyze(district: District, map: Map) -> None:
    average: ivec3 = district.average()
    average_height: int = average.y
    water_blocks = 0
    leaf_blocks = 0
    neighbour_height = 0
    number_of_points: int = len(district.points)
    district.biome_dict = {}
    district.surface_blocks = {}

    root_mean_square_height = 0

    for point in district.points:
        biome: str = map.biome_at(ivec2(point.x, point.z))
        block: str = map.block_at(ivec2(point.x, point.z)).id
        water: bool = map.water_at(ivec2(point.x, point.z))
        leaf_height: int = map.height_at_include_leaf(ivec2(point.x, point.z))

        root_mean_square_height += pow(point.y - average_height, 2)
        # ugly code to prevent from crashing on getting out of bounds error
        height: int = point.y
        with contextlib.suppress(IndexError):
            height = map.height_no_tree[point.x][point.z]
        n1 = n2 = n3 = n4 = height

        neighbour_height += (
            abs(point.y - n1)
            + abs(point.y - n2)
            + abs(point.y - n3)
            + abs(point.y - n4)
        ) / 4

        if biome not in district.biome_dict:
            district.biome_dict[biome] = 1
        else:
            district.biome_dict[biome] += 1

        if block not in district.surface_blocks:
            district.surface_blocks[block] = 1
        else:
            district.surface_blocks[block] += 1

        if water:
            water_blocks += 1
        elif point.y != leaf_height:
            # discrepancy between height map including leaves and normal height = leaves above block
            leaf_blocks += 1

    # root mean square
    district.roughness = math.sqrt(root_mean_square_height / number_of_points)
    # average difference of neighbour block height
    district.gradient = neighbour_height / number_of_points
    district.water_percentage = water_blocks / number_of_points
    district.forested_percentage = leaf_blocks / number_of_points


def _choose_more_urban_district(
    district1: Type[District], district2: Type[District]
) -> Type[District]:
    roughness_difference: float = district1.roughness - district2.roughness
    gradient_difference: float = (district1.gradient - district2.gradient) / 3
    forest_difference: float = (
        district1.forested_percentage - district2.forested_percentage
    )
    water_difference: float = district1.water_percentage - district2.water_percentage
    overall_difference: float = (
        roughness_difference
        + gradient_difference
        + forest_difference
        + water_difference
    )
    return district2 if overall_difference > 0 else district1


def district_classification(districts: list[District]) -> None:

    # select prime urban spot
    prime_urban_district: District | None = None

    # determine if district is unbuildable
    for district in districts:

        if district.is_border or district.roughness > 6 or district.gradient > 1.0:
            district.type = DistrictType.OFF_LIMITS
            continue

        if district.type is None and district.water_percentage <= 0.33:
            prime_urban_district = (
                district
                if prime_urban_district is None
                else _choose_more_urban_district(prime_urban_district, district)
            )

    if prime_urban_district is None:
        raise RuntimeError("Could not establish a prime urban district!")

    prime_urban_district.type = DistrictType.URBAN

    # check each district (regardless of adjacency for compatibility to be urban in relation to prime)
    for district in districts:
        if district.type is None:
            score: float = get_candidate_score_no_adjacency(
                prime_urban_district, district
            )
            if score > BEST_SCORE:
                district.type = DistrictType.URBAN
            else:
                district.type = DistrictType.RURAL


# assumes the child districts have already been classified
def super_district_classification(districts: list[SuperDistrict]) -> None:
    # set deterministic district types
    # select prime urban spot

    prime_urban_district: SuperDistrict | None = None
    for district in districts:

        if district.is_border:
            district.type = DistrictType.OFF_LIMITS
            continue

        score: float = district.get_subtypes_score()
        if score > 1.5:
            district.type = DistrictType.OFF_LIMITS
        elif score > 0.5:
            district.type = DistrictType.RURAL
        elif (
            prime_urban_district is None
            or score < prime_urban_district.get_subtypes_score()
        ):
            prime_urban_district = district
        elif score == prime_urban_district.get_subtypes_score():
            prime_urban_district = _choose_more_urban_district(
                prime_urban_district, district
            )

    if prime_urban_district is None:
        raise RuntimeError("Could not establish a prime urban district!")

    prime_urban_district.type = DistrictType.URBAN
    urban_districts: list[SuperDistrict] = [prime_urban_district]
    urban_count = 1
    # expand out city from prime urban districts
    while urban_count < URBAN_SIZE:
        # get options
        option_set: set[District] = set()
        for district in urban_districts:
            neighbours: list[District] = district.get_adjacent_districts()
            for neighbour in neighbours:
                if neighbour.type is None:
                    option_set.add(neighbour)

        # All options already vetted as being urban possible
        best_score: float = -1
        best: SuperDistrict | None = None

        for district in option_set:
            score = get_candidate_score(prime_urban_district, district)
            if score > best_score:
                best = district
                best_score = score

        if best is None:
            break

        best.type = DistrictType.URBAN
        urban_districts.append(best)
        urban_count += 1

    # rest is rural
    for district in districts:
        if district.type is None:
            district.type = DistrictType.RURAL


def get_candidate_score(
    district: District, candidate: District, use_adjacency: bool = True
) -> float:
    # NOTE: option to add some hard limits to scores, where below a certain score in a category it is flat out rejected

    ADJACENCY_WEIGHT = 3

    adjacency_score: float = 0.0
    if use_adjacency:
        adjacency_score = (
            1000.0 * district.get_adjacency_ratio(candidate) / float(candidate.area)
        )

    biome_score = 1 - sum(
        abs(
            district.biome_dict[key] / district.area
            - candidate.biome_dict.get(key, 0) / candidate.area
        )
        for key in district.biome_dict.keys()
    ) / len(district.biome_dict.keys())

    water_score: float = 1 - abs(district.water_percentage - candidate.water_percentage)

    forest_score: float = 1 - abs(
        district.forested_percentage - candidate.forested_percentage
    )

    gradient_score: float = 1 - abs(district.gradient - candidate.gradient) / 2

    roughness_score: float = 1 / (abs(district.roughness - candidate.roughness) + 1)

    return (
        adjacency_score * ADJACENCY_WEIGHT
        + biome_score
        + water_score
        + forest_score
        + gradient_score
        + roughness_score
    ) / (5 + use_adjacency * ADJACENCY_WEIGHT)


def get_candidate_score_no_adjacency(district: District, candidate: District) -> float:

    return get_candidate_score(district, candidate, False)
