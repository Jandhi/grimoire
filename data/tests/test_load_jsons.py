# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\data\\tests')

# Actual file
from data.load_jsons import load_jsons, load_objects

class Test:
    field : str

print(load_jsons('data/tests'))

test : Test = load_objects('data/tests', Test)[0]

print(test.field)