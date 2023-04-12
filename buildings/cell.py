
from dataclasses import dataclass
from structures.directions import direction, vector
from gdpc.vector_tools import ivec3
from buildings.roofs.roof_data import RoofData

# Class to store data for cells in a building grid
@dataclass
class Cell:
    position : ivec3
    roof_data : RoofData
    plan : any # will be a building plan

    def has_neighbour(self, direction : direction):
        return self.position + vector(direction) in self.plan.cells 
    
    def get_neighbour(self, direction : direction):
        pt = self.position + vector(direction)

        if pt not in self.plan.cells:
            return None

        return self.plan.cells[pt]