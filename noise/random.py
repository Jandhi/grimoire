    
from .seed import Seed, seed_function

@seed_function
def randint(seed : Seed, ceiling : int) -> int:
    return seed.value() % ceiling

@seed_function
def odds(seed : Seed, success : int, failure : int) -> bool:
    return randint(seed, success + failure) < success

@seed_function
def chance(seed : Seed, success : int, total : int) -> bool:
    return randint(seed, total) < success