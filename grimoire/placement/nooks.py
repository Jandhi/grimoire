import itertools
from enum import Enum, auto
from logging import error, warn
from typing import Any, Callable, Generator, Iterable, Sequence, TypeVar

from gdpc.editor import Editor
from gdpc.vector_tools import CARDINALS_2D, Rect, neighbors2D
from glm import ivec2

from grimoire.core.maps import DevelopmentType, Map
from grimoire.core.noise.rng import RNG
from grimoire.core.styling.palette import BuildStyle
from grimoire.core.utils.misc import to_list_or_none
from grimoire.core.utils.shapes import Shape2D
from grimoire.districts.district import DistrictType
from grimoire.placement.terraformers.texture import (
    flagstone_edge,
    grass_patch_area,
    pave_over_area,
    roughen_edge,
)
from grimoire.placement.terraformers.topology import flatten_area_up

LOOP_LIMIT = 16  # prevents uncontrolled loops from going on too long


class TrafficExposureType(Enum):
    UNSURE = auto()  # an error state
    ISLAND = auto()  # surrounded by streets
    PENINSULA = auto()  # mainly surrounded by streets
    COVE = auto()  # mainly surrounded by buildings
    CHANNEL = auto()  # connects two streets
    COURT = auto()  # not surrounded by any streets


DEFAULT_TRAFFIC_EXPOSURE = TrafficExposureType.UNSURE


class WaterExposureType(Enum):
    DRY = auto()  # contains no water
    POND = auto()  # contains a closed body of water within the nook
    LAKE = auto()  # contains a freshwater body which extends beyond the nook
    STREAM = auto()  # is divided by a freshwater body
    WETLAND = auto()  # is in a wetland biome (e.g. swamp)
    RIVER = auto()  # is in a river biome
    COAST = auto()  # is in a coastal biome
    OCEAN = auto()  # is in an ocean biome


DEFAULT_WATER_EXPOSURE = WaterExposureType.POND


class DevelopmentPattern:

    def __init__(self):
        self.shape = Shape2D()

    def calculate_pattern(
        self, edge_development_map: dict[ivec2, set[DevelopmentType]]
    ):
        self.shape.update(set(edge_development_map.keys()))
        # scan from smallest to largest coordinates
        for x, z in itertools.product(
            range(self.shape.begin.x, self.shape.end.x),
            range(self.shape.begin.y, self.shape.end.y),
        ):
            if ivec2(x, z) in edge_development_map:
                # TODO: Check neighbours for similar developments, merge if sensible
                raise NotImplementedError


class Nook:
    """
    Represents a decorative Nook which takes up odd spaces in the world.
    It may be fitted with constraints to guide placement, but will not check these constraints when manifesting.

    NOTE: The value "None" means the Nook is suitable for all values of that contraint.

    Args:
        district_types: The district types this was designed for.
        exposure_types: The exposure types this was designed for.
        min_rect: Minimum rectangular space recommended.
        max_rect: Maximum rectangular space recommended.
        min_area: Minimum area recommended.
        max_area: Maximum area recommended.
        styles: The styles this Nook fit into.
        terraformers: The terraformers to be executed sequentially.
        decorators: The decorators to be executed sequentially.
        surface: Surface or None.
        edging: Edging or None.

    """

    def __init__(
        self,
        name: str,
        district_types: DistrictType | Iterable[DistrictType] | None = None,
        exposure_types: (
            TrafficExposureType | Iterable[TrafficExposureType] | None
        ) = None,
        styles: BuildStyle | Iterable[BuildStyle] | None = None,
        min_area: int | None = None,
        max_area: int | None = None,
        min_rect: Rect | None = None,
        max_rect: Rect | None = None,
        terraformers: (
            Iterable[
                Callable[
                    [
                        Editor,
                        Shape2D,
                        dict[ivec2, set[DevelopmentType]],
                        Map,
                        RNG,
                    ],
                    Any,
                ]
            ]
            | None
        ) = None,
        decorators: (
            Iterable[
                Callable[
                    [
                        Editor,
                        Shape2D,
                        dict[ivec2, set[DevelopmentType]],
                        Map,
                        RNG,
                    ],
                    Any,
                ]
            ]
            | None
        ) = None,
    ) -> None:
        self.name = name
        self.district_types = district_types
        self.exposure_types = exposure_types
        self.styles = styles
        self.min_area = min_area
        self.max_area = max_area
        self.min_rect = min_rect
        self.max_rect = max_rect
        self.terraformers = terraformers
        self.decorators = decorators

    def manifest(
        self,
        editor: Editor,
        area: Shape2D,
        edges: dict[ivec2, set[DevelopmentType]],
        city_map: Map,
        rng: RNG,
    ) -> None:
        """
        Execute the Nook's terraformers and decorators with the given parameters.

        Args:
            editor: The Editor object for terraforming.
            area: The Shape2D area to terraform.
            edges: A dictionary of edges.
            city_map: The Map object representing the city map.
            rng: The RNG object for random number generation.

        Returns:
            None
        """

        for position in area | set(edges.keys()):
            city_map.buildings[position.x][position.y] = DevelopmentType.NOOK

        # the processing stages and the parameters of the functions in that stage
        STAGES: list[tuple[Iterable[Callable] | None, list]] = [
            (
                self.terraformers,
                [editor, area, edges, city_map, rng],
            ),
            (self.decorators, [editor, area, edges, city_map, rng]),
        ]

        for stage, parameters in STAGES:
            if stage is not None:
                for processor in stage:
                    processor(*parameters)

        return


def identify_exposure_type_from_edging_pattern(
    pattern: Sequence[tuple[set[DevelopmentType], int]],
) -> TrafficExposureType:
    if not pattern:
        warn(
            f"Provided pattern was empty. Defaulting to '{DEFAULT_TRAFFIC_EXPOSURE.name}'."
        )
        return DEFAULT_TRAFFIC_EXPOSURE

    PATHS: frozenset[DevelopmentType] = frozenset(
        {
            DevelopmentType.CITY_ROAD,
            DevelopmentType.HIGHWAY,
            DevelopmentType.GATE,
        }
    )
    BUILDINGS: frozenset[DevelopmentType] = frozenset(
        {
            DevelopmentType.BUILDING,
            DevelopmentType.CITY_WALL,
            DevelopmentType.WALL,
        }
    )
    development_sets = (PATHS, BUILDINGS, frozenset({DevelopmentType.NOOK}))

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
        if broad_pattern[0][0] == PATHS:
            return TrafficExposureType.ISLAND
        if broad_pattern[0][0] == BUILDINGS:
            return TrafficExposureType.COURT

    totals: dict[frozenset[DevelopmentType], int] = {
        development_set: 0 for development_set in development_sets
    }

    for broad_segment in broad_pattern:
        totals[broad_segment[0]] += broad_segment[1]

    if (
        len(broad_pattern) < 4
    ):  # two segment (one segment may be split between begininng and end)
        if totals[PATHS] > totals[BUILDINGS]:
            return TrafficExposureType.PENINSULA
        return TrafficExposureType.COVE

    return TrafficExposureType.CHANNEL


# ==== Instances ====
HIGH_EXPOSURE: list[TrafficExposureType] = [
    TrafficExposureType.CHANNEL,
    TrafficExposureType.ISLAND,
    TrafficExposureType.PENINSULA,
]
MIXED_EXPOSURE: list[TrafficExposureType] = [
    TrafficExposureType.PENINSULA,
    TrafficExposureType.COVE,
]
LOW_EXPOSURE: list[TrafficExposureType] = [
    TrafficExposureType.COURT,
    TrafficExposureType.COVE,
]

PATCHY_PAVED_NOOK = Nook(
    "Patchy Paving",
    exposure_types=HIGH_EXPOSURE,
    terraformers=[pave_over_area, roughen_edge],
)
PATCHY_GRASS_NOOK = Nook(
    "Patchy Grass",
    exposure_types=LOW_EXPOSURE,
    terraformers=[grass_patch_area, roughen_edge],
)
GRASSY_YARD_NOOK = Nook(
    "Grassy Yard",
    exposure_types=MIXED_EXPOSURE,
    terraformers=[grass_patch_area, flagstone_edge],
)
PLATEAU_NOOK = Nook(
    "Plateau",
    district_types=DistrictType.URBAN,
    terraformers=[flatten_area_up, pave_over_area],
)

ALL_NOOKS = {PATCHY_PAVED_NOOK, PATCHY_GRASS_NOOK, GRASSY_YARD_NOOK, PLATEAU_NOOK}

DEFAULT_NOOK = PATCHY_GRASS_NOOK

# ==== Nook Sets ====


def _set_from_type_iterable(
    nook_type_iter: Iterable,
    nook: Nook,
    values: Any,
    nook_type_dict: dict[Any, set[Nook]] | None = None,
) -> dict[Any, set[Nook]]:
    if not nook_type_dict:
        nook_type_dict = {t: set() for t in nook_type_iter}
    else:
        for t in nook_type_iter:
            if t not in nook_type_dict:
                nook_type_dict[t] = set()

    if values is None:  # add the nook to all sets
        for nook_type_set in nook_type_dict.values():
            nook_type_set.add(nook)
    elif isinstance(values, Iterable):  # add the nook to multiple sets
        for nook_type in values:
            nook_type_dict[nook_type].add(nook)
    elif values in nook_type_iter:  # add the nook to a single set
        nook_type_dict[nook.district_types].add(nook)
    else:
        raise ValueError(f"{values} is not a valid type for evaluation!")
    return nook_type_dict


NOOKS_BY_DISTRICT: dict[DistrictType, set[Nook]] = {}
NOOKS_BY_EXPOSURE: dict[TrafficExposureType, set[Nook]] = {}
NOOKS_BY_STYLE: dict[str, set[Nook]] = {}

for nook in ALL_NOOKS:
    NOOKS_BY_DISTRICT = _set_from_type_iterable(
        DistrictType, nook, nook.district_types, NOOKS_BY_DISTRICT
    )
    NOOKS_BY_EXPOSURE = _set_from_type_iterable(
        TrafficExposureType, nook, nook.exposure_types, NOOKS_BY_EXPOSURE
    )
    NOOKS_BY_STYLE = _set_from_type_iterable(
        BuildStyle, nook, nook.styles, NOOKS_BY_STYLE
    )
    NOOKS_BY_WATER = _set_from_type_iterable(
        WaterExposureType, nook, nook.styles, NOOKS_BY_STYLE
    )


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


def find_suitable_nooks(
    district_types: DistrictType | Iterable[DistrictType] | None = None,
    exposure_types: TrafficExposureType | Iterable[TrafficExposureType] | None = None,
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
    _exposure_types: list[TrafficExposureType] | None = to_list_or_none(exposure_types)
    _styles: list[BuildStyle] | None = to_list_or_none(styles)

    type_sets: list[tuple[list[T] | None, dict[T, set[Nook]]]] = [
        (_district_types, NOOKS_BY_DISTRICT),
        (_exposure_types, NOOKS_BY_EXPOSURE),
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
        for neighbor in neighbors2D(point, bounds):
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

    for direction in CARDINALS_2D:
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
