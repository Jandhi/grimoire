from gdpc.vector_tools import ivec2, ivec3

class District:
    average : ivec2
    origin : ivec2
    sum : ivec3
    count : int
    inner : bool

    def __init__(self, origin : ivec2, inner) -> None:
        self.origin = origin
        self.sum = ivec3(0, 0, 0)
        self.count = 0
        self.inner = inner

    def add_block(self, block_coord : ivec3):
        self.sum += block_coord
        self.count += 1

    def print(self):
        print(self.origin, self.sum, self.count, self.inner)