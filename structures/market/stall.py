from structures.directions import Direction
from random import seed
from random import randint
from structures.market.goods import *

class Stall:

    #p1 and p2 are the starting and end points of the rectangle that forms the road
    def __init__(self, origin, counter: str = 'basic', side: str = 'basic', roof: str = 'basic', overhang: str = 'none', direction: Direction = 'z_minus', length: int=5, depth: int = 4, height: int = 5) -> None:
        self.origin = origin
        self.overhang = overhang
        self.counter = counter
        self.roof = roof
        self.side = side
        self.direction = direction
        self.length = length
        self.depth = depth
        self.height = height
        self.back_counter = False #should there be a duplicate counter at the rear of the stall
        self.counter_space = [] #list of points where there is space to put items on a counter
        self.floor_space = [] #list of points where there is space to put items on a floor
        self.palette : dict = {}

        if self.counter == 'random':
            self.randomize_stall()

        if self.side == 'none' or self.side == 'trapdoor' or self.side == 'fence_gate':
            seed()
            chance_of_back_counter = randint(1,5)
            if chance_of_back_counter < 5:
                self.back_counter = True

        self.goods = 'none'
        self.set_random_goods()

        self.randomize_colour()
        

    def get_origin(self):
        return self.origin

    def set_origin(self, origin):
        self.origin = origin

    def set_direction(self, direction):
        self.direction = direction

    def add_counter_space(self, point):
        self.counter_space.append(point)

    def add_floor_space(self, point):
        self.floor_space.append(point)

    def get_floor_good(self):
        seed()
        list_of_goods = self.goods.floor_goods
        a = randint(0, len(list_of_goods)-1)
        return list_of_goods[a]

    def get_counter_good(self):
        seed()
        list_of_goods = self.goods.counter_goods
        a = randint(0, len(list_of_goods)-1)
        return list_of_goods[a]

    def has_floor_goods(self):
        if self.goods.floor_goods == False:
            return False
        return True

    def set_random_goods(self):
        seed()
        a = randint(0,16) #start at 0 if you want a chance of empty stalls
        if a == 1:
            self.goods = Flower_Shop()
        elif a == 2:
            self.goods = Plant_Shop()
        elif a == 3:
            self.goods = Head_Shop() #heads don't face correctly atm
        elif a == 4:
            self.goods = Wool_Shop()
        elif a == 5:
            self.goods = Glazed_Terracotta_Shop()
        elif a == 6:
            self.goods = Glass_Shop()
        elif a == 7:
            self.goods = Shulker_Shop()
        elif a == 8:
            self.goods = Fruit_Shop()
        elif a == 9:
            self.goods = Armour_Shop()
        elif a == 10:
            self.goods = Bakery_Shop()
        elif a == 11:
            self.goods = Bell_Pepper_Shop()
        elif a == 12:
            self.goods = Japanese_Shop()
        elif a == 13:
            self.goods = Honey_Shop()
        elif a == 14:
            self.goods = Donut_Shop()
        elif a == 15:
            self.goods = Butcher_Shop()
        elif a == 16:
            self.goods = Alcohol_Shop()

    def randomize_stall(self):
        seed()
        a = randint(1,6)
        if a == 1:
            self.counter = 'basic'
        elif a == 2:
            self.counter = 'half_stair'
        elif a == 3:
            self.counter = 'stair'
        elif a == 4:
            self.counter = 'half_slab'
        elif a == 5:
            self.counter = 'stair_slab'
        elif a == 6:
            self.counter = 'slab'

        seed()
        a = randint(1,6)
        if a == 1:
            self.side = 'basic'
        elif a == 2:
            self.side = 'fence'
        elif a == 3:
            self.side = 'fence_gate'
        elif a == 4:
            self.side = 'trapdoor'
        elif a == 5:
            self.side = 'stair'
        elif a == 6:
            self.side = 'slab'

        seed()
        a = randint(1,6)
        if a == 1:
            self.roof = 'basic'
        elif a == 2:
            self.roof = 'back_down'
        elif a == 3:
            self.roof = 'sides_down'
        elif a == 4:
            self.roof = 'front_down'
        elif a == 5:
            self.roof = 'front_back_down'

        seed()
        a = randint(1,4)
        if a == 1:
            self.overhang = 'none'
        elif a == 2:
            self.overhang = 'trapdoor'
        elif a == 3:
            self.overhang = 'banner'
        elif a == 4:
            self.overhang = 'campfire'
        
    def randomize_colour(self):
        seed()
        colour_list = ('red', 'white', 'orange', 'magenta','light_blue', 'yellow', 'lime', 'pink', 'gray', 'light_gray', 'cyan',
            'blue', 'purple', 'brown', 'green', 'black')
        a = randint(0, len(colour_list)-1)
        choice1 = colour_list[a]
        self.palette['market_wool_1'] = f'{choice1}_wool'
        self.palette['market_banner_1'] = f'{choice1}_wall_banner'
        seed()
        a = randint(0, len(colour_list)-1)
        choice2 = colour_list[a]
        self.palette['market_wool_2'] = f'{choice2}_wool'
        self.palette['market_banner_2']  = f'{choice2}_wall_banner'