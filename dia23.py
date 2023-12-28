import random
from functools import cache
from collections import deque

from copy import copy

class GoalReached(Exception):
    pass


class V2(tuple):
    def __new__(cls, x, y=None):
        if y != None:
            x = (x, y)
        return super().__new__(cls, x)

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    def __add__(self, other):
        return type(self)((self.x + other[0], self.y + other[1]))

    __radd__ = __add__

    def __sub__(self, other):
        return type(self)(self.x - other[0], self.y - other[1])

    def __eq__(self, other):
        if not hasattr(other, "__len__") or len(other) != 2:
            return False
        return self[0] == other[0] and self[1] == other[1]

    def __hash__(self):
        return hash(tuple(self))

    def __neg__(self):
        return type(self)(-self.x, -self.y)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y})"

    def manhattan(self, other):
        return abs(self[0] - other[0]) + abs(self[1] - other[1])


NORTH = V2(0, -1)
WEST = V2(-1, 0)
SOUTH = V2(0, 1)
EAST = V2(1, 0)

DIRECTIONS = {
    "^": NORTH,
    "<": WEST,
    ">": EAST,
    "v": SOUTH,
}

dirmap = {  # ['←', '↑', '→', '↓']
    NORTH: "↑",
    WEST: "←",
    SOUTH: "↓",
    EAST: "→",
    V2(0, 0): "@",
}


class History:
    def __init__(self, pos, prev=None):
        self.prev = prev
        self.pos = pos
        self.length = (len(prev) + 1) if prev else 1
        self.cache = prev.cache if prev else set()
        self.has_cache = self.length % 350 == 0
        if self.has_cache:
            cache = copy(self.cache)
            cache.update(item for i, item in zip(range(351), self))
            self.cache = cache

    def __add__(self, other: V2):
        return type(self)(other, self)

    def __iter__(self):
        yield self.pos
        prev = self.prev
        while prev:
            yield prev.pos
            prev = prev.prev

    def __len__(self):
        return self.length

    @cache
    def __contains__(self, pos):
        if pos == self.pos:
            return True
        prev = self.prev
        while prev:
            if prev.has_cache:
                return pos in prev.cache
            if pos == prev.pos:
                return True
            prev = prev.prev
        return False

    def __repr__(self):
        return repr(list(self))

class Walker:
    id = 0

    def __new__(cls, *args, **kw):
        self = super().__new__(cls)
        cls.id += 1
        self.id = cls.id
        return self

    def __init__(self, map, initial, last_pos=None, weight=0):
        self.map = map
        self.color = random.choice(range(41, 47))
        self.pos = initial
        self.last_pos = last_pos
        self.weight = weight
        self.map[self.pos].weight = weight
        self.map[self.pos].walker = self
        self.map[self.pos].walker_last_pos = self.last_pos
        self.tree = set()
        self.alive = True

    def step(self):
        if not self.alive:
            print(f"\nArghhh {self.pos}...")
            return []
        if self.pos == (ep:=self.map.ending_pos):
            print (f"\nBingo: ", self.weight)
            if self.map[ep].weight is None or self.weight > self.map[ep].weight:
                self.map[ep].weight = self.weight
            return []
        new_walkers = []
        weight = self.weight + 1
        #if weight == 16:
            #breakpoint()
        orig_pos = self.pos
        orig_history = getattr(self, "history", None)
        for direction in DIRECTIONS.values():
            target = orig_pos + direction
            if target == self.last_pos: continue
            if not self.map.inrange(target): continue
            if (cell:=self.map[target]).is_wall: continue
            if self.check_direction(cell, direction): continue
            if self.check_history(target): continue
            if self.check_weight(cell, weight, orig_pos):
                extra = {"history": orig_history + target} if hasattr(self, "history") else {}
                if hasattr(cell, "walker") and cell.walker_last_pos == orig_pos and cell.weight and cell.weight < weight and cell.walker.alive:
                    breakpoint()
                    cell.walker.kill()
                if len(new_walkers) or orig_history is None:
                    new_walker = type(self)(self.map, target, last_pos=orig_pos, weight=weight, **extra)
                    new_walkers.append(new_walker)
                    self.tree.add(new_walker)
                else:
                    self.weight = weight
                    self.pos = target
                    if hasattr(self, "history"):
                        self.history += target
                    new_walkers.append(self)
                    cell.weight = weight
                    cell.walker = self
                    cell.walker_last_pos = orig_pos

        return new_walkers

    def kill(self):
        self.alive = False
        for w in self.tree:
            w.kill()

    #def check_weight(self, cell, weight):
        #if (w:=cell.weight) is None:
            #return True


    def check_weight(self, cell, weight, orig_pos):
        if cell.weight is None:
            return True
        if cell.weight < weight:
            return True
        return False


    def check_history(self, target):
        return False

    def check_direction(self, cell, direction):
        if cell.direction is None:
            return False
        if cell.direction != direction:
            return True
        return False

    def __str__(self):
        return f"Walker \x1b[{self.color}m#{self.id}\x1b[40m!"

    def __repr__(self):
        return f"Walker {self.id}"

    def __eq__(self, other):
        return self.weight == other.weight and self.pos == other.pos and self.last_pos == other.last_pos

    def __hash__(self):
        return hash((self.weight, self.pos, self.last_pos))



class WalkerPart2(Walker):
    def __init__(self, map, initial, last_pos=None, weight=0, history=None):
        if history is None:
            self.history = History(initial)
        else:
            self.history = history
        super().__init__(map, initial, last_pos, weight)

    def check_history(self, target):
        if target in self.history:
            return True
        return False

    def check_weight(self, cell, weight, orig_pos):
        if not (r:=super().check_weight(cell, weight, orig_pos)):
            if cell.walker_last_pos != orig_pos:
                return True

        return r



    #def __eq__(self, other):
        #return super().__eq__(other) and len(self.history) == len(other.history)

    #def __hash__(self):
        #return hash((super().__hash__(), len(self.history)))

    def check_direction(self, cell, direction):
        return False

class Cell:
    def __init__(self, char):
        if isinstance(char, type(self)):
            char = char.char
        self.char = char
        self.direction = DIRECTIONS.get(char, None)
        self.is_wall = char == "#"

        self.weight: "Optional[int]" = None

    def __repr__(self):
        return self.char


class Map:
    def __init__(self, data: str, threshold=3):
        self.threshold = threshold
        self.load(data)
        self.reset()

    def reset(self):
        self.walkers: list[Walker] = []
        for y in range(self.height):
            for x in range(self.width):
                self[x,y].weight = None

    def load(self, data):
        lines = data.split("\n")
        self.data = [[Cell(char) for char in line] for line in lines]
        self.width = len(self.data[0])
        self.height = len(self.data)
        self.starting_pos = V2(lines[0].find("."), 0)
        self.ending_pos = V2(lines[-1].find("."), self.height - 1)

    def inrange(self, pos):
        return 0 <= pos[0] < self.width and 0 <= pos[1] < self.height

    #def set_weight(self, walker):
        #self.weights[walker.pos] = WeightState(walker)

    def __getitem__(self, pos):
        if not self.inrange(pos):
            raise IndexError()
        return self.data[pos[1]][pos[0]]

    def __setitem__(self, pos, val):
        self.data[pos[1]][pos[0]] = Cell(val)

    def print(self):
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                if self[x, y].is_wall:
                    line += "####"
                elif self[x,y].weight is None:
                    line += "    "
                else:
                    line += f"{self[x,y].weight:^4d}"
            print(line)

    def walk(self, walker_class=Walker):
        self.reset()
        self.walkers = {walker_class(self, self.starting_pos),}
        while self.walkers:
            new_walkers = []
            for walker in self.walkers:
                new_walkers.extend(walker.step())
            self.walkers = set(new_walkers)
            #for x in self.walkers:
                #if new_walkers.count(x) > 1:
                    #breakpoint()
            print("\rupdate: ", len(self.walkers), new_walkers[-1].pos if new_walkers else "bingo", end="    ", flush=True)
        return self.result


    def doit(self, print=True):
        self.walk()
        if print:
            self.print()
        return self.result

    def doit_part2(self, print=True):
        self.walk(walker_class=WalkerPart2)
        if print:
            self.print()
        return self.result

    @property
    def result(self):
        return self[self.ending_pos].weight

    def __repr__(self):
        return "\n".join("".join(str(w) for w in line) for line in self.data)
