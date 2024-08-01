from enum import Enum, auto

from gdpc.vector_tools import ivec2, ivec3

from grimoire.core.styling.palette import Palette
from grimoire.core.utils.sets.find_outer_points import find_edges_2D


class DistrictType(Enum):
    URBAN = auto()
    RURAL = auto()
    OFF_LIMITS = auto()


class DistrictType(Enum):
    URBAN = auto()
    RURAL = auto()
    OFF_LIMITS = auto()


class District:
    id_counter = 0
    id: int
    points: set[ivec3]
    points_2d: set[ivec2]
    origin: ivec3
    sum: ivec3
    area: int
    adjacency: dict["District", int]
    edges: set[ivec3]
    adjacencies_total: int
    type: DistrictType
    is_border: bool
    parent_id: int

    palettes: list[Palette]
    roughness: float
    biome_dict: dict[str, int]
    water_percentage: float
    forested_percentage: float
    surface_blocks: dict[str, int]
    gradient: float

    def __init__(self, origin: ivec3) -> None:
        self.id = District.id_counter
        District.id_counter += 1

        self.origin = origin
        self.sum = ivec3(0, 0, 0)
        self.area = 0
        self.adjacency = {}
        self.points = set()
        self.points_2d = set()
        self.edges = set()
        self.adjacencies_total = 0
        self.is_border = False
        self.palettes = []
        self.roughness = 0
        self.biome_dict = {}
        self.water_percentage = 0
        self.forested_percentage = 0
        self.surface_blocks = {}
        self.gradient = 0
        self.type: DistrictType | None = None
        self.parent_id: int | None = None

        self._add_point(origin)

    def _recenter(self, origin) -> None:

        self.origin = origin
        self.sum = ivec3(0, 0, 0)
        self.area = 0
        self.adjacency = {}
        self.points = set()
        self.points_2d = set()
        self.edges = set()
        self.adjacencies_total = 0
        self.palettes = []

        self._add_point(origin)

    def _add_point(self, point: ivec3) -> None:
        self.points.add(point)
        self.points_2d.add(ivec2(point.x, point.z))
        self.sum += point
        self.area += 1

    def _add_adjacency(self, district: "District") -> None:
        if district not in self.adjacency:
            self.adjacency[district] = 0

        self.adjacencies_total += 1
        self.adjacency[district] += 1

    def get_adjacency(self, district) -> int:
        return 0 if district not in self.adjacency else self.adjacency[district]

    def get_adjacent_districts(self) -> list["District"]:
        return list(self.adjacency.keys())

    def get_adjacency_ratio(self, district) -> float:
        return float(self.get_adjacency(district)) / float(self.adjacencies_total)

    def __repr__(self) -> str:
        return f"district {self.id}"

    def average(self) -> ivec3:
        return sum(self.points) / len(self.points)


class SuperDistrict(District):
    districts: list[District]

    def __init__(self, district: District) -> None:
        self.districts = [district]
        super().__init__(district.origin)
        self.sum = district.sum
        self.area = district.area
        self.adjacency = {}
        self.points = district.points.copy()
        self.points_2d = district.points_2d.copy()
        self.edges = set()
        self.adjacencies_total = 0
        self.is_border = district.is_border
        self.palettes = district.palettes
        self.roughness = district.roughness
        self.biome_dict = district.biome_dict
        self.water_percentage = district.water_percentage
        self.forested_percentage = district.forested_percentage
        self.surface_blocks = district.surface_blocks
        self.gradient = district.gradient
        self.type = district.type

        # child gets parent set
        district.parent_id = self.id

    def get_subtypes(self) -> dict[DistrictType, int]:
        subtypes: dict[DistrictType, int] = {}
        for district in self.districts:
            if district.type not in subtypes:
                subtypes[district.type] = 1
            else:
                subtypes[district.type] += 1
        return subtypes

    def get_subtypes_score(self) -> float:
        subtypes: dict[DistrictType, int] = self.get_subtypes()
        return (
            subtypes.get(DistrictType.OFF_LIMITS, 0) * 2  # keyerror
            + subtypes.get(DistrictType.RURAL, 0) * 1
            # NOTE: This is unnecessary: + subtypes[DistrictType.URBAN] * 0
        ) / len(self.districts)
