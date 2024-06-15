import itertools
from enum import Enum, auto
from logging import error, warn
from typing import Any, Callable, Iterable

from gdpc.editor import Editor
from gdpc.vector_tools import Rect
from glm import ivec2

from grimoire.core.maps import DevelopmentType, Map
from grimoire.core.noise.rng import RNG
from grimoire.core.styling.palette import BuildStyle
from grimoire.core.utils.misc import to_list_or_none
from grimoire.core.utils.shapes import Shape2D
from grimoire.districts.district import DistrictType
from grimoire.placement.nooks.terraformers.edging import simple_closed_fencing
from grimoire.placement.nooks.terraformers.texture import (
    central_statue,
    flagstone_edge,
    fully_paved,
    fully_paved_desert,
    grass_edge,
    grass_patch_area,
    roughen_edge,
    trees_in_area,
    wild_growth_area,
)

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

    instances: set["Nook"] = set()

    def __init__(
        self,
        name: str,
        district_types: DistrictType | Iterable[DistrictType] | None = None,
        traffic_exposure_types: (
            TrafficExposureType | Iterable[TrafficExposureType] | None
        ) = None,
        water_exposure_types: (
            WaterExposureType | Iterable[WaterExposureType] | None
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
        self.district_types = to_list_or_none(district_types)
        self.traffic_exposure_types = to_list_or_none(traffic_exposure_types)
        self.water_exposure_types = to_list_or_none(water_exposure_types)
        self.styles = to_list_or_none(styles)
        self.min_area = min_area
        self.max_area = max_area
        self.min_rect = min_rect
        self.max_rect = max_rect
        self.terraformers = terraformers
        self.__class__.instances.add(self)

    def specificity(self):
        ADDITIVE_VALUES = [
            self.district_types,
            self.traffic_exposure_types,
            self.water_exposure_types,
            self.styles,
        ]
        RANGE_VALUES = [(self.min_area, self.max_area), (self.min_rect, self.max_rect)]

        score = sum(len(v) for v in ADDITIVE_VALUES if v)
        score += sum(
            max(3, 3 - (max_v // min_v // 10)) if min_v and max_v else 1
            for min_v, max_v in RANGE_VALUES
            if min_v or max_v
        )

        return score

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
        ]

        for stage, parameters in STAGES:
            if stage is not None:
                for processor in stage:
                    processor(*parameters)

        return


HIGH_EXPOSURE: frozenset[TrafficExposureType] = frozenset(
    {
        TrafficExposureType.CHANNEL,
        TrafficExposureType.ISLAND,
        TrafficExposureType.PENINSULA,
    }
)
MIXED_EXPOSURE: frozenset[TrafficExposureType] = frozenset(
    {
        TrafficExposureType.PENINSULA,
        TrafficExposureType.COVE,
    }
)
LOW_EXPOSURE: frozenset[TrafficExposureType] = frozenset(
    {
        TrafficExposureType.COURT,
        TrafficExposureType.COVE,
    }
)

# ==== NOOK DEFINITION ====

# PATCHY_PAVED_NOOK = Nook(
#     "Patchy Paving",
#     exposure_types=HIGH_EXPOSURE,
#     terraformers=[pave_over_area, roughen_edge],
# )
NORMAL_SQUARE_NOOK = Nook(
    "Square",
    traffic_exposure_types=HIGH_EXPOSURE,
    styles=BuildStyle.NORMAL_MEDIEVAL,
    terraformers=[fully_paved, roughen_edge],
)
MONUMENT_NOOK = Nook(
    "Monument",
    traffic_exposure_types=TrafficExposureType.ISLAND,
    styles=[BuildStyle.NORMAL, BuildStyle.NORMAL_MEDIEVAL],
    min_area=30,
    min_rect=Rect(size=(5, 5)),
    terraformers=[fully_paved, roughen_edge, central_statue],
)
DESERT_PLAZA_NOOK = Nook(
    "Desert Plaza",
    traffic_exposure_types=HIGH_EXPOSURE,
    styles=BuildStyle.DESERT,
    terraformers=[fully_paved_desert, roughen_edge],
)
PATCHY_GRASS_NOOK = Nook(
    "Patchy Grass",
    terraformers=[
        grass_patch_area,
        grass_edge,
        roughen_edge,
        wild_growth_area,
        trees_in_area,
    ],
)
GRASSY_YARD_NOOK = Nook(
    "Grassy Yard",
    traffic_exposure_types=MIXED_EXPOSURE,
    terraformers=[
        grass_patch_area,
        flagstone_edge,
        wild_growth_area,
        simple_closed_fencing,
        trees_in_area,
    ],
)
FENCED_WILD_GARDEN_NOOK = Nook(
    "Fenced Wild Garden",
    traffic_exposure_types=MIXED_EXPOSURE,
    terraformers=[
        grass_patch_area,
        grass_edge,
        roughen_edge,
        wild_growth_area,
        simple_closed_fencing,
        trees_in_area,
    ],
)
# PLATEAU_NOOK = Nook(
#     "Plateau",
#     district_types=DistrictType.URBAN,
#     terraformers=[flatten_area_up, pave_over_area],
# )


# ==== NOOK SETS ====

NOOKS_BY_DISTRICT: dict[DistrictType, set[Nook]] = {}
NOOKS_BY_TRAFFIC_EXPOSURE: dict[TrafficExposureType, set[Nook]] = {}
NOOKS_BY_WATER_EXPOSURE: dict[WaterExposureType, set[Nook]] = {}
NOOKS_BY_STYLE: dict[BuildStyle, set[Nook]] = {}


DEFAULT_NOOK = PATCHY_GRASS_NOOK


def categorise_nooks():
    """Categorise all Nooks into their appropriate positions of the Nook Sets."""

    global NOOKS_BY_DISTRICT
    global NOOKS_BY_TRAFFIC_EXPOSURE
    global NOOKS_BY_WATER_EXPOSURE
    global NOOKS_BY_STYLE

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
            nook_type_dict[values].add(nook)
        else:
            raise ValueError(f"{values} is not a valid type for evaluation!")
        return nook_type_dict

    for nook in Nook.instances:
        NOOKS_BY_DISTRICT = _set_from_type_iterable(
            DistrictType, nook, nook.district_types, NOOKS_BY_DISTRICT
        )
        NOOKS_BY_TRAFFIC_EXPOSURE = _set_from_type_iterable(
            TrafficExposureType,
            nook,
            nook.traffic_exposure_types,
            NOOKS_BY_TRAFFIC_EXPOSURE,
        )
        NOOKS_BY_WATER_EXPOSURE = _set_from_type_iterable(
            WaterExposureType, nook, nook.water_exposure_types, NOOKS_BY_WATER_EXPOSURE
        )
        NOOKS_BY_STYLE = _set_from_type_iterable(
            BuildStyle, nook, nook.styles, NOOKS_BY_STYLE
        )


categorise_nooks()
