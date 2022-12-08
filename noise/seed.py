import types
from typing import Callable
from noise.munge import munge
from functools import partial

class Seed:
    seed_functions = {}

    def __init__(self, value) -> None:
        if isinstance(value, int):
            self.__value = value
        elif isinstance(value, Seed):
            self.__value = value.value()
        else:
            self.__value = hash(value)
        
        self.__add_functions__()

    def __add_functions__(self) -> None:
        for (name, val) in Seed.seed_functions.items():
            self.__setattr__(name, partial(val, self))
    
    def value(self) -> int:
        return self.__value

    def __mul__(self, other):
        if not isinstance(other, Seed):
            other = Seed(other)

        return Seed(munge(self.__value, other.__value))

    def randint(self, ceiling : int) -> int:
        pass

    def odds(self,  success : int, failure : int) -> bool:
        pass

    def chance(self, success : int, total : int) -> bool:
        pass

def seed_function(function):
    Seed.seed_functions[function.__name__] = function
    return function