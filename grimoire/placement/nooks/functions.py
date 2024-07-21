from logging import error, warn
from typing import Any, Generator, Iterable, Sequence, TypeVar

from gdpc.vector_tools import CARDINALS_AND_DIAGONALS_2D, Rect, ivec2, neighbors2D

from grimoire.core.maps import (
    BUILDING_DEVELOPMENTS,
    PATH_DEVELOPMENTS,
    DevelopmentType,
    Map,
)
from grimoire.core.noise.rng import RNG
from grimoire.core.styling.palette import BuildStyle
from grimoire.core.utils.misc import to_list_or_none
from grimoire.core.utils.shapes import Shape2D
from grimoire.districts.district import DistrictType
from grimoire.placement.nooks.nook import (
    DEFAULT_NOOK,
    DEFAULT_TRAFFIC_EXPOSURE,
    NOOKS_BY_DISTRICT,
    NOOKS_BY_STYLE,
    NOOKS_BY_TRAFFIC_EXPOSURE,
    NOOKS_BY_WATER_EXPOSURE,
    Nook,
    TrafficExposureType,
    WaterExposureType,
)

LOOP_LIMIT = 16


def identify_traffic_exposure_from_edging_pattern(
    pattern: Sequence[tuple[set[DevelopmentType], int]],
) -> TrafficExposureType:
    # TODO: Simplify traffic exposure to be based on % of surrounding developments
    if not pattern:
        warn(
            f"Provided pattern was empty. Defaulting to '{DEFAULT_TRAFFIC_EXPOSURE.name}'."
        )
        return DEFAULT_TRAFFIC_EXPOSURE

    development_sets = (
        PATH_DEVELOPMENTS,
        BUILDING_DEVELOPMENTS,
        frozenset({DevelopmentType.NOOK}),
    )

    # TODO: Split this into another function
    broad_pattern: list[tuple[frozenset[DevelopmentType], int]] = []

    # Meld the pattern into fewer segments
    # NOTE: This is a very basic approach and may have to be improved!
    for segment in pattern:
        for development in segment[0]:
            # Add a new segment on a first-come, first-serve basis
            if not broad_pattern or development not in broad_pattern[-1][0]:
                for development_set in development_sets:
                    if development in development_set:
                        broad_pattern.append(
                            (
                                frozenset(development_set),
                                segment[1],
                            )
                        )
                        break
                else:  # This development is not covered in the sets, try another
                    continue
            else:  # We're continuing an established segment, update the tuple
                broad_pattern[-1] = (
                    broad_pattern[-1][0],
                    broad_pattern[-1][1] + segment[1],
                )
            break
        else:
            raise RuntimeError(
                f"None of the following elements are covered by development sets!\n\t{segment[0]}"
            )

    if not broad_pattern:
        warn(
            f"Did not generate a broad pattern. Defaulting to '{DEFAULT_TRAFFIC_EXPOSURE.name}'"
        )
        return DEFAULT_TRAFFIC_EXPOSURE

    if len(broad_pattern) < 2:  # a single segment
        if broad_pattern[0][0] == PATH_DEVELOPMENTS:
            return TrafficExposureType.ISLAND
        if broad_pattern[0][0] == BUILDING_DEVELOPMENTS:
            return TrafficExposureType.COURT

    totals: dict[frozenset[DevelopmentType], int] = {
        development_set: 0 for development_set in development_sets
    }

    for broad_segment in broad_pattern:
        totals[broad_segment[0]] += broad_segment[1]

    if (
        len(broad_pattern) < 4
    ):  # two segment (one segment may be split between begininng and end)
        if totals[PATH_DEVELOPMENTS] > totals[BUILDING_DEVELOPMENTS]:
            return TrafficExposureType.PENINSULA
        return TrafficExposureType.COVE

    return TrafficExposureType.CHANNEL


def eliminate_nooks_based_on_area(nook_set: set[Nook], area: Shape2D) -> set[Nook]:

    nook_set_copy: set[Nook] = nook_set.copy()
    for nook in nook_set_copy:
        if (nook.min_area is not None and nook.min_area > len(area)) or (
            nook.max_area is not None and nook.max_area < len(area)
        ):  # if the Nook is not suitable for the area
            nook_set.remove(nook)
    return nook_set


def eliminate_nooks_based_on_largest_rect(nook_set, area: Shape2D) -> set[Nook]:
    rect: Rect = area.get_largest_rect()
    raise NotImplementedError()


def choose_suitable_nook(
    rng: RNG,
    district_types: DistrictType | Iterable[DistrictType] | None = None,
    traffic_exposure_types: (
        TrafficExposureType | Iterable[TrafficExposureType] | None
    ) = None,
    water_exposure_types: WaterExposureType | Iterable[WaterExposureType] | None = None,
    styles: BuildStyle | Iterable[BuildStyle] | None = None,
    area: Shape2D | None = None,
):
    candidates = find_suitable_nooks(
        district_types, traffic_exposure_types, water_exposure_types, styles, area
    )
    candidate_string = "\n\t\t\t- ".join(
        [f"{c.name:24}:{c.specificity()}" for c in candidates]
    )
    print(f"\t\tNook candidates are:\n\t\t\t- {candidate_string}")
    return rng.choose_weighted({n: max(1, n.specificity()) for n in candidates})


def find_suitable_nooks(
    district_types: DistrictType | Iterable[DistrictType] | None = None,
    traffic_exposure_types: (
        TrafficExposureType | Iterable[TrafficExposureType] | None
    ) = None,
    water_exposure_types: WaterExposureType | Iterable[WaterExposureType] | None = None,
    styles: BuildStyle | Iterable[BuildStyle] | None = None,
    area: Shape2D | None = None,
) -> set[Nook]:
    """
    Finds suitable Nooks based on the provided constraints.
    None means that the value will be ignored.

    Args:
        district_types: District types or None.
        exposure_types: Exposure types or None.
        styles: Styles or None.
        available_area: Available area or None.
        available_rect: Available rectangle or None.

    Returns:
        A set of suitable Nooks.
    """

    T = TypeVar("T")

    def update_set_from_enum(
        type_list: list[T] | None, nook_set: dict[T, set[Nook]]
    ) -> set[Nook] | None:

        if type_list is None:  # skip this type list
            return None

        stepwise_set = set()
        for i_type in type_list:
            stepwise_set.update(nook_set[i_type])

        return stepwise_set

    def update_final_set(
        final_set: set[Nook] | None, update_set: set[Nook] | None
    ) -> set[Nook] | None:
        """Update the final set of Nooks with the update set.

        Arguments:
            final_set: The current final set
            update_set: The update set with new values to be used or intersected.

        Returns:
            The updated final set.
        """

        if update_set is None:  # This type list should be skipped
            pass
        # Otherwise, update the final set
        elif final_set is None:
            final_set = update_set
        else:
            final_set &= update_set  # Intersect it with the new results
        return final_set

    _district_types: list[DistrictType] | None = to_list_or_none(district_types)
    _traffic_exposure_types: list[TrafficExposureType] | None = to_list_or_none(
        traffic_exposure_types
    )
    _water_exposure_types: list[WaterExposureType] | None = to_list_or_none(
        water_exposure_types
    )
    _styles: list[BuildStyle] | None = to_list_or_none(styles)

    type_sets: list[tuple[list[T] | None, dict[T, set[Nook]]]] = [
        (_district_types, NOOKS_BY_DISTRICT),
        (_traffic_exposure_types, NOOKS_BY_TRAFFIC_EXPOSURE),
        (_water_exposure_types, NOOKS_BY_WATER_EXPOSURE),
        (_styles, NOOKS_BY_STYLE),
    ]

    final_set: set[Nook] | None = None

    # goes through all type sets to establish and quickly eliminate candidates
    for type_list, nook_set in type_sets:
        final_set = update_final_set(
            final_set, update_set_from_enum(type_list, nook_set)
        )

        if final_set == set():  # There are no more candidates left
            final_set = None
            break

    # No candidates were established in the first place. Return an empty set.
    if final_set is None:
        warn(f"Could not find suitable Nook. Defaulting to {DEFAULT_NOOK.name}.")
        return {DEFAULT_NOOK}

    if area is not None:
        final_set = eliminate_nooks_based_on_area(final_set, area)
        # TODO: final_set = eliminate_nooks_based_on_largest_rect(final_set, area)

    return final_set


# ==== Nook discovery ====


def discover_nook(
    start: ivec2, city_block_shape: Shape2D, city_map: Map
) -> tuple[set[ivec2], Shape2D]:
    """Find the extent of a potential Nook in a city block, starting at a free space."""

    development_map: list[list[DevelopmentType | None]] = city_map.buildings
    valid_rect = city_block_shape.to_rect()
    bounding_rect = city_block_shape.to_boundry_rect()

    if development_map[start.x][start.y] is not None:
        raise ValueError(
            f"Start ({start}) must be unoccupied in the city map (is {development_map[start.x][start.y]})"
        )

    nook_edge: set[ivec2] = set()
    nook_area = Shape2D()

    stack: list[ivec2] = [start]
    visited: set[ivec2] = set()

    # trace the nook, returning its edge and non-edge area
    while stack:
        position = stack.pop()

        if position in visited:
            continue

        visited.add(position)

        if development_map[position.x][position.y]:
            continue

        for neighbor in neighbors2D(position, bounding_rect, diagonal=True):

            # has a developed neighbour
            if development_map[neighbor.x][neighbor.y] or not valid_rect.contains(
                neighbor
            ):
                visited.add(neighbor)
                nook_edge.add(position)

            if neighbor not in visited:
                stack.append(neighbor)

        # did not have a developed neighbour
        if position not in nook_edge:
            nook_area.add(position)

    return nook_edge, nook_area


def map_developments_at_edge(
    edge: set[ivec2], city_map: Map, bounds: Rect
) -> dict[ivec2, set[DevelopmentType]]:
    development_set: dict[ivec2, set[DevelopmentType]] = {}
    for point in edge:
        for neighbor in neighbors2D(point, bounds, diagonal=True):
            if development := city_map.buildings[neighbor.x][neighbor.y]:
                if point not in development_set:
                    development_set[point] = set()
                development_set[point].add(development)

    return development_set


def edge_to_pattern(
    start: ivec2, edge: dict[ivec2, set[DevelopmentType]], bounds: Rect
) -> list[tuple[set[DevelopmentType], int]]:

    edge_start: ivec2 = ivec2(start)

    if not edge:
        return []

    pattern: list[tuple[set[DevelopmentType], int]] = []

    for direction in CARDINALS_AND_DIAGONALS_2D:
        edge_start = ivec2(start)
        for _ in range(LOOP_LIMIT):
            if edge_start in edge:
                break
            edge_start += direction
        else:
            continue
        break
    else:
        raise RuntimeError(
            f"Could not find an edge to the Nook originating from {start} (intervened at {edge_start})."
        )

    for current in determine_edge_sequence(start, bounds, edge):

        if current not in edge:
            error(
                f"Current position {current} is not a valid edge value! It is being skipped."
            )
            continue

        if not pattern or edge[current] != pattern[-1][0]:  # new pattern segment
            pattern.append((edge[current], 1))
            continue
        pattern[-1] = (pattern[-1][0], pattern[-1][1] + 1)  # extend current segment

    return pattern


def determine_edge_sequence(
    start: ivec2, bounds: Rect, edge: Iterable[ivec2]
) -> Generator[ivec2, Any, None]:
    current_position: ivec2 = start
    visited: set[ivec2] = set()

    stack = [start]

    while stack:
        current_position = stack.pop()
        yield current_position
        visited.add(current_position)

        for neighbor in neighbors2D(current_position, bounds):
            if neighbor in edge and neighbor not in visited:
                stack.append(neighbor)

    return
