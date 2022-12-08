from typing import Union
from noise.generator_seed import GeneratorSeed

class Node:
    def __init__(self, item = None, weight = 0) -> None:
        self.left_child : Node = None
        self.right_child : Node = None
        self.weight = weight
        self.is_leaf = False if item is None else True
        self.item = item

class MagicHat:
    def __init__(self, seed) -> None:
        self.generator = GeneratorSeed(seed)
        self.root = Node()

    def add(self, item, weight):
        self.__add_to_node(item, weight, self.root)

    def __add_to_node(self, item, weight, node):
        parent : Node = node
        
        if parent.is_leaf:
            parent.is_leaf = False
            parent.left_child = Node(parent.item, parent.weight)
            parent.right_child = Node(item, weight)
            parent.item = None
            parent.weight += weight
            return

        parent.weight += weight

        if parent.left_child is None:
            parent.left_child = Node(item, weight)
            parent.count += 1
            return
        
        if parent.right_child is None:
            parent.right_child = Node(item, weight)
            parent.count += 1
            return

        if parent.left_child.weight > parent.right_child.weight:
            return self.__add_to_node(item, weight, parent.left_child)
        else:
            return self.__add_to_node(item, weight, parent.right_child)
                
    
    def remove(self):
        pass