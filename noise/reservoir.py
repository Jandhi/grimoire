from noise.random import odds


class Reservoir:
    def __init__(self, seed) -> None:
        self.seed = seed
        self.total_weight = 0
        self.count = 0
        self.item = None
    
    def add_item(self, item, weight):
        if odds(self.seed * self.count, weight, self.total_weight):
            self.item = item
        
        self.count += 1
        self.total_weight += weight
        return self.item