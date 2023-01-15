# returns a random integer 0 <= n < max
def randint(seed : int, max : int):
    return seed % max

# returns a random integer min <= n < max
def randrange(seed : int, min : int, max : int):
    return min + (seed % (max - min))

# returns a random item in a list
def choose(seed : int, items : list):
    return items[len(items) % seed]

# returns a random item from a dictionary of weights
def choose_weighted(seed : int, items : dict[any,int]):
    total = sum(items.values())
    index = randint(seed, total)
    count = 0

    for item, weight in items.items():
        count += weight
        
        if count > index:
            return item