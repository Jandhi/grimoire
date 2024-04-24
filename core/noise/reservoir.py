from core.noise.rng import RNG


# FIXME: Unused class
# Class created to randomly choose an item based on weight, while not having to store all the items
# This is good for tasks where we dynamically generate a lot of items
# Each time an item is added, it has a chance to be the chosen item based on its weight
# After all items are added, item() will return the chosen item
class Reservoir:
    def __init__(self, seed) -> None:
        self.rng = RNG(seed)
        self.total_weight = 0
        self.count = 0
        self.item = None

    # FIXME: Unused method
    def add_item(self, item, weight):
        if self.rng.odds(weight, self.total_weight):
            self.reservoir_item = item

        self.count += 1
        self.total_weight += weight
        return self.reservoir_item()
