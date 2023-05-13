from data.asset import Asset
from gdpc.vector_tools import ivec3

class BuildingShape(Asset):
    points : list[ivec3]

    def on_construct(self) -> None:
        self.points = [
            ivec3(x, y, z) for (x, y, z) in self.points
        ]