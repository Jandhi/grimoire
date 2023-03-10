from gdpc.vector_tools import ivec2, ivec3

class District:
    average : ivec2
    origin : ivec2
    sum : ivec3
    count : int

    def __init__(self, origin : ivec2) -> None:
        self.origin = origin
        self.sum = ivec3(0, 0, 0)
        self.count = 0

    def add_block(self, block_coord : ivec3):
        self.sum += block_coord
        self.count += 1