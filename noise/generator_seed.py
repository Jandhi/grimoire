from noise.munge import munge
from noise.seed import Seed

class GeneratorSeed(Seed):
    def __init__(self, value) -> None:
        super().__init__(value)
        self.counter = 0
    
    def value(self) -> int:
        value = munge(self.__value, self.counter)
        
        if self.counter == 0:
            value = self.__value

        self.counter += 1

        return value