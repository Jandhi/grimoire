from re import S
from noise.reservoir import Reservoir
from noise.seed import Seed
from noise.random import chance

x = 1
seed = Seed(3321)
r = seed.randint(5)
print(r)
r = seed.chance(5, 10)
print(r)
r = seed.odds(5, 10)
print(r)