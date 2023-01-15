from noise.hash import hash
from noise.seed import Seed

# determenistic random number generator with state
class RNG(Seed):
    def __init__(self, seed) -> None:
        self.seed = seed
        self.state = 0

    def next(self) -> int:
        val = hash(self.seed, self.state)
        self.state += 1
        return val

    def value(self) -> int:
        return next()