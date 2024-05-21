from gdpc.vector_tools import ivec2, ivec3
from palette.palette import Palette

class District:
    id_counter = 0
    id : int
    points : set[ivec3]
    points_2d : set[ivec2]
    origin : ivec3
    sum : ivec3
    area : int
    adjacency : dict[any, int]
    edges : set[ivec3]
    adjacencies_total : int
    is_urban : bool
    type: str #URBAN/RURAL/OFF-LIMITS
    is_border : bool
    parent_id: int

    roughness: float
    biome_dict: dict[str, int]
    water_percentage: float
    forested_percentage: float
    surface_blocks: dict[str, int]
    gradient: float

    def __init__(self, origin : ivec3) -> None:
        self.id = District.id_counter
        District.id_counter += 1
        
        self.origin = origin
        self.sum = ivec3(0, 0, 0)
        self.area = 0
        self.adjacency = {}
        self.points    = set()
        self.points_2d = set()
        self.edges     = set()
        self.adjacencies_total = 0
        self.is_urban = False
        self.is_border = False
        self.palettes = []
        self.roughness = 0
        self.biome_dict = {}
        self.water_percentage = 0
        self.forested_percentage = 0
        self.surface_blocks = {}
        self.gradient = 0
        self.type = None
        self.parent_id = None

        self.add_point(origin)

    def recenter(self, origin) -> None:
    
        self.origin = origin
        self.sum = ivec3(0, 0, 0)
        self.area = 0
        self.adjacency = {}
        self.points    = set()
        self.points_2d = set()
        self.edges     = set()
        self.adjacencies_total = 0
        self.palettes = []

        self.add_point(origin)

    def add_point(self, point : ivec3):
        self.points.add(point)
        self.points_2d.add(ivec2(point.x, point.z))
        self.sum += point
        self.area += 1

    def add_adjacency(self, district):
        if district not in self.adjacency:
            self.adjacency[district] = 0
        
        self.adjacencies_total += 1
        self.adjacency[district] += 1
    
    def get_adjacency(self, district):
        if district not in self.adjacency:
            return 0
        
        return self.adjacency[district]
    
    def get_adjacent_districts(self) -> list:
        return list(self.adjacency.keys())
    
    def get_adjacency_ratio(self, district) -> float:
        return float(self.get_adjacency(district)) / float(self.adjacencies_total)
    
    def __repr__(self) -> str:
        return f'district {self.id}'
    
    def average(self) -> ivec3:
        return sum(self.points) / len(self.points)
    
class SuperDistrict(District):
    districts : list[District]

    def __init__(self, district: District) -> None:
        self.districts = [district]
        super().__init__(district.origin)
        self.sum = district.sum
        self.area = district.area
        self.adjacency = {}
        self.points    = district.points.copy()
        self.points_2d = district.points_2d.copy()
        self.edges     = set()
        self.adjacencies_total = 0
        self.is_urban = district.is_urban
        self.is_border = district.is_border
        self.palettes = district.palettes
        self.roughness = district.roughness
        self.biome_dict = district.biome_dict
        self.water_percentage = district.water_percentage
        self.forested_percentage = district.forested_percentage
        self.surface_blocks = district.surface_blocks
        self.gradient = district.gradient
        self.type = district.type

        #child gets parent set
        district.parent_id = self.id

    def get_subtypes(self): 
        subtypes = dict()
        for district in self.districts:
            if district.type not in subtypes:
                subtypes[district.type] = 1
            else:
                subtypes[district.type] += 1
        return subtypes
    
    def get_subtypes_score(self):
        subtypes = self.get_subtypes()
        score = (subtypes.get('OFF-LIMITS', 0)*2 + subtypes.get('RURAL', 0)*1 + subtypes.get('URBAN', 0)*0) / len(self.districts)
        return score