def add_tuples(*tuples : tuple) -> tuple:
    return map_tuple(sum, zip(*tuples))

def multiply_tuple(tup : tuple, amount : int) -> tuple:
    return tuple(amount * item for item in tup)

def sub_tuples(t1 : tuple, t2 : tuple) -> tuple:
    return map_tuple(lambda x : x[0] - x[1], zip(t1, t2))

def map_tuple(fn : callable, t1 : tuple) -> tuple:
    return tuple(map(fn, t1))

# Takes in N tuples, and some fn which reduces N items to 1
# Returns that item for each index
def map_tuples(fn : callable, *tuples : tuple) -> tuple:
    return tuple(map(lambda items : fn(*items), zip(*tuples)))