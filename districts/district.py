from gdpc.vector_tools import ivec2, ivec3

class District:
    id_counter = 0
    id : int
    average : ivec2
    origin : ivec2
    sum : ivec3
    area : int
    adjacency : dict[any,int]
    edges : set[ivec2]
    adjacencies_total : int
    is_urban : bool

    def __init__(self, origin : ivec2, is_urban : bool) -> None:
        self.id = District.id_counter
        District.id_counter += 1
        
        self.origin = origin
        self.sum = ivec3(0, 0, 0)
        self.area = 0
        self.adjacency = {}
        self.edges = set()
        self.adjacencies_total = 0
        self.is_urban = is_urban

    def add_block(self, block_coord : ivec3):
        self.sum += block_coord
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