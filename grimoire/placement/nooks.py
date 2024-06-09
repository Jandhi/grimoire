import itertools
from enum import Enum, auto
from logging import warn
from typing import Any, Callable, Iterable, Sequence, TypeVar

from gdpc.editor import Editor
from gdpc.vector_tools import Rect
from glm import ivec2

from grimoire.core.maps import DevelopmentType, Map
from grimoire.core.noise.rng import RNG
from grimoire.core.styling.materials.material import Material
from grimoire.core.styling.palette import BuildStyle
from grimoire.core.utils.misc import to_list_or_none
from grimoire.core.utils.shapes import Shape2D
from grimoire.districts.district import DistrictType
from grimoire.placement.terraformers.texture import grass_patch_area, pave_over_area
from grimoire.placement.terraformers.topology import flatten_area_up


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


class ExposureType(Enum):
    ISLAND = auto()
    PENINSULA = auto()
    COVE = auto()
    CHANNEL = auto()
    COURT = auto()


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
        district_types: DistrictType | Iterable[DistrictType] | None = None,
        exposure_types: ExposureType | Iterable[ExposureType] | None = None,
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
) -> ExposureType:
    PATHS: set[DevelopmentType] = {
        DevelopmentType.CITY_ROAD,
        DevelopmentType.HIGHWAY,
        DevelopmentType.GATE,
    }
    BUILDINGS: set[DevelopmentType] = {
        DevelopmentType.BUILDING,
        DevelopmentType.CITY_WALL,
        DevelopmentType.WALL,
    }
    development_sets = (PATHS, BUILDINGS)

    # TODO: Split this into another function
    broad_pattern: list[tuple[set[DevelopmentType], int]] = []

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
                                development_set,
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

    if broad_pattern == []:
        warn("Did not generate a broad pattern. Defaulting to 'COURT'")
        return ExposureType.COURT

    if len(broad_pattern) < 2:  # a single segment
        if broad_pattern[0][0] == PATHS:
            return ExposureType.ISLAND
        if broad_pattern[0][0] == BUILDINGS:
            return ExposureType.COURT

    # calculate dominant sets
    totals: dict[set[DevelopmentType], int] = {}
    for segment in broad_pattern:
        if segment[0] not in totals:
            totals[segment[0]] = segment[1]
        else:
            totals[segment[0]] += segment[1]

    if (
        len(broad_pattern) < 4
    ):  # two segment (one segment may be split between begininng and end)
        if totals[PATHS] > totals[BUILDINGS]:
            return ExposureType.PENINSULA
        return ExposureType.COVE

    return ExposureType.CHANNEL


# ==== Instances ====
HIGH_EXPOSURE: list[ExposureType] = [
    ExposureType.CHANNEL,
    ExposureType.ISLAND,
    ExposureType.PENINSULA,
]
LOW_EXPOSURE: list[ExposureType] = [ExposureType.COURT, ExposureType.COVE]

PAVED_NOOK = Nook(exposure_types=HIGH_EXPOSURE, terraformers=[pave_over_area])
GRASSY_NOOK = Nook(exposure_types=LOW_EXPOSURE, terraformers=[grass_patch_area])
PLATEAU = Nook(
    district_types=DistrictType.URBAN, terraformers=[flatten_area_up, pave_over_area]
)

ALL_NOOKS = {PAVED_NOOK, GRASSY_NOOK, PLATEAU}

# ==== Nook Sets ====


def _set_from_type_iterable(
    nook_type_iter: Iterable, nook: Nook, values: Any
) -> dict[Any, set[Nook]]:
    nook_type_dict: dict[Any, set] = {t: set() for t in nook_type_iter}

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


for nook in ALL_NOOKS:
    NOOKS_BY_DISTRICT: dict[DistrictType, set[Nook]] = _set_from_type_iterable(
        DistrictType, nook, nook.district_types
    )
    NOOKS_BY_EXPOSURE: dict[ExposureType, set[Nook]] = _set_from_type_iterable(
        ExposureType, nook, nook.exposure_types
    )
    NOOKS_BY_STYLE: dict[str, set[Nook]] = _set_from_type_iterable(
        BuildStyle, nook, nook.styles
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
    exposure_types: ExposureType | Iterable[ExposureType] | None = None,
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
    _exposure_types: list[ExposureType] | None = to_list_or_none(exposure_types)
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
        warn("Could not find suitable Nook. Defaulting to GRASSY_NOOK.")
        return {GRASSY_NOOK}

    if area is not None:
        final_set = eliminate_nooks_based_on_area(final_set, area)
        # TODO: final_set = eliminate_nooks_based_on_largest_rect(final_set, area)

    return final_set
