# returns a random integer 0 <= n < max
def randint(seed : int, max : int) -> int:
    return seed % max

# returns a random integer min <= n < max
def randrange(seed : int, min : int, max : int) -> int:
    return min + (seed % (max - min))

# returns a random item in a list
def choose(seed : int, items : list):
    return items[seed % len(items)]

# returns a random item from a dictionary of weights
def choose_weighted(seed : int, items : dict[any,int]):
    total = sum(items.values())
    index = randint(seed, total)
    count = 0

    for item, weight in items.items():
        count += weight
        
        if count > index:
            return item

# randomly determines value based on ratio of successes to failures
def odds(seed : int, successes : int, failures : int) -> bool:
    return randint(seed, successes + failures) < successes

# randomly determines value based on successes to total chance
def chance(seed : int, successes : int, total : int) -> bool:
    return randint(seed, total) < successes

# returns a shuffled copy of the list
def shuffle(seed : int, items : list) -> list:
    copied_list = items.copy()
    new_list = []

    while len(copied_list) > 0:
        length = len(copied_list)
        index = randint(hash(seed, length), length)
        new_list.append(copied_list.pop(index))
    
    return new_list