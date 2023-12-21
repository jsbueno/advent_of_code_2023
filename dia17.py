import random
from dataclasses import dataclass

class V2(tuple):
    def __new__(cls, x, y = None):
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

    def __sub__(self, other):
        return type(self)(self.x - other[0], self.y - other[1])

    def __eq__(self, other):
        return self[0] == other[0] and self[1] == other[1]
    def __hash__(self):
        return hash(tuple(self))

    def __neg__(self):
        return type(self)(-self.x, -self.y)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y})"



NORTH = V2(0, -1)
WEST = V2(-1, 0)
SOUTH = V2(0, 1)
EAST = V2(1, 0)
DIRECTIONS = (NORTH, WEST, SOUTH, EAST)

dirmap = { #['←', '↑', '→', '↓']
    NORTH: "↑",
    WEST: "←",
    SOUTH: "↓",
    EAST: "→",
    V2(0, 0): "@",
}

#@dataclass
class WeightState:
    pos: V2
    previous_pos: V2
    weight: int
    color: int
    walker_id: int
    dead_at_beach: bool

    def __init__(self, walker):
        self.pos = walker.pos
        self.previous_pos = walker.history[-2] if len(walker.history) >= 2 else V2(0,0)
        self.weight = walker.weight
        self.color = walker.color
        self.walker_id = walker.id
        self.dead_at_beach = walker.check_straight(walker.map.threshold, walker.history, walker.pos + self.last_direction)

    @property
    def last_direction(self):
        return self.pos - self.previous_pos


class Walker:
    id = 0
    restrict = None
    sleep = None
    def __new__(cls, *args):
        self = super().__new__(cls)
        cls.id += 1
        self.id = cls.id
        return self

    def __init__(self, map, initial):
        self.map = map
        self.color = random.choice(range(41, 47))
        self.history = [initial]
        self.weight = 0
        self.map.set_weight(self)

    @property
    def pos(self):
        return self.history[-1]

    def clone(self, pos, history, weight):
        walker = type(self).__new__(type(self))
        walker.map = self.map
        walker.history = history[:] + [pos]
        walker.weight = weight
        walker.color = random.choice(range(41, 47))
        return walker

    def walk_or_fork(self, walkers, pos, history, weight):
        if not walkers:
            self.history += [pos]
            self.weight = weight
            new_walker = self
        else:
            new_walker = self.clone(pos, history, weight)
        if new_walker.restrict:
            del new_walker.restrict
        walkers.append(new_walker)
        return new_walker

    def check_straight(self, threshold, history, pos):
        if len(history) < threshold:
            return False
        direction = pos - history[-1]
        return all((history[-1-i] - history[-2-i]) == direction  for i in range(threshold - 1))

    @property
    def direction(self):
        if len(self.history) < 2:
            return V2(0,0)
        return self.history[-1] - self.history[-2]

    def step(self):
        new_walkers = []
        if self.sleep:
            self.sleep -= 1
            if self.sleep == 0:
                self.slept = True
            return [self]
        #if  self.map.weights[self.pos].walker_id != self.id:
            #return ()
        history = self.history[:]
        prev_weight = self.weight
        prev_pos = self.pos
        if self.restrict:
            directions = [self.restrict]
        else:
            if (xy:=self.direction) != V2(0,0):
                directions = list(DIRECTIONS[(xx:=DIRECTIONS.index(xy)):] + DIRECTIONS[:xx])
            else:
                directions = list(DIRECTIONS)
        if (xy:=-self.direction) in  directions:
            directions.remove(xy)
        for direction in directions:
            whereto = prev_pos + direction
            if not self.map.inrange(whereto):# or whereto in history[-3:]:
                continue
            if self.check_straight(self.map.threshold, history, whereto):
                #if not getattr(self, "slept", None):
                    #self.slept = False
                    #self.sleep = 20
                    #return [self]
                continue
            #if len(self.history) >=2 and whereto == self.history[-2]:
                #continue
            weight = prev_weight + self.map[whereto]
            dest = self.map.weights.get(whereto, None)

            if not dest or dest.weight > weight:
                new_walker = self.walk_or_fork(new_walkers, whereto, history, weight)
                self.map.set_weight(new_walker)
            elif dest.weight <= weight and dest.dead_at_beach and direction != dest.last_direction:
                new_walker = self.walk_or_fork(new_walkers, whereto, history, weight)
                new_walker.restrict = dest.last_direction
        return new_walkers


    def __str__(self):
        return f"Walker \x1b[{self.color}m#{self.id}\x1b[40m!"
    def __repr__(self):
        return f"Walker {self.id}"

class Map:
    threshold = 3

    def __init__(self, data:str):
        self.load(data)
        self.reset()

    def reset(self):
        self.walkers: list[Walker] = []
        self.weights: dict[V2, WeightState] = {}

    def load(self, data):
        self.data = [[int(num) for num in line] for line in data.split("\n")]
        self.width = len(self.data[0])
        self.height = len(self.data)

    def inrange(self, pos):
        return 0 <= pos[0] < self.width and 0 <= pos[1] < self.height

    def set_weight(self, walker):
        self.weights[walker.pos] = WeightState(walker)


    def __getitem__(self, pos):
        if not self.inrange(pos):
            raise IndexError()
        return self.data[pos[1]][pos[0]]

    def __setitem__(self, pos, val):
        self.data[pos[1]][pos[0]] = val

    def walk(self, startpos=V2(0,0)):
        self.reset()
        self.walkers = [Walker(self, startpos)]
        yield
        while  self.walkers:
            new_walkers = []
            for walker in self.walkers:
                new_walkers.extend(walker.step())
            yield
            self.walkers = new_walkers
        return self.result

    def print(self, done=False):
        print("\x1b[H\x1b[0J", end="")
        done_path = set()
        if done:
            pos = V2(self.width - 1, self.height - 1)
            done_path.add(pos)
            while pos != V2(0,0):
                pos = self.weights[pos].previous_pos
                done_path.add(pos)
        for y in range(self.height):
            for x in range(self.width):
                pos = V2(x,y)
                if info:=self.weights.get(pos):
                    print(f"\x1b[{info.color if pos not in done_path else 47}m", end="")
                else:
                    color = None
                what = self[pos] if not (info:=self.weights.get(pos, None)) else dirmap[info.last_direction] if not info.dead_at_beach else "#" if pos not in done_path else "*"
                print(what, end="")
                if info:
                    print("\x1b[49m", end="")
            print()

    def doit(self, print=True):
        w = self.walk()
        while True:
            try:
                next(w)
                if print:
                    self.print()
            except StopIteration as v:
                return v.value

    @property
    def result(self):
        return self.weights[self.width - 1, self.height - 1].weight

    def __repr__(self):
        return "\n".join("".join(str(w) for w in line) for line in self.data)


