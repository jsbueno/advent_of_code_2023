import random
from functools import cache
from collections import deque
import time

from copy import copy

class GoalReached(Exception):
    pass

def sgn(num):
    return -1 if num < 0 else 0 if num == 0 else 1

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

    def __rsub__(self, other):
        return type(self)(other[0] - self.x, other[1] - self.y)

    def __eq__(self, other):
        if not hasattr(other, "__len__") or len(other) != 2:
            return False
        return self[0] == other[0] and self[1] == other[1]

    def __mul__(self, other):
        return type(self)(other * self.x, other * self.y)

    __rmul__ = __mul__

    def __hash__(self):
        return hash(tuple(self))

    def __neg__(self):
        return type(self)(-self.x, -self.y)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y})"

    def manhattan(self, other):
        return abs(self[0] - other[0]) + abs(self[1] - other[1])


class Rect:
    def __init__(self, c1, c2):
        # close ended at c2: final corner _is_part_ of rect.
        self.c1 = V2(min(c1[0], c2[0]), min(c1[1], c2[1]))
        self.c2 = V2(max(c1[0], c2[0]), max(c1[1], c2[1]))

    def __contains__(self, pos):
        return self.c1.x <= pos[0] <= self.c2.x and self.c1.y <= pos[1] <= self.c2.y

    def linerange(self, c1, c2):
        # open endded at C2 last cell, like "range"
        direction = c2 - c1
        if direction.x != 0 and direction.y != 0:
            raise ValueError("linerange can only operate in vertical or horizontal lines")

        step = V2(sgn(direction.x), sgn(direction.y))

        pos = c1
        while pos != c2:
            yield pos
            pos += step

    def iter_wall(self, roi: "Rect"=None):
        c1, c2 = self.c1, self.c2
        if c1 == c2:
            yield c1
            return
        for side in (
            self.linerange(V2(c1.x, c2.y - 1), c1),
            self.linerange(c1, (c2.x, c1.y)),
            self.linerange(V2(c2.x, c2.y), c2),
            self.linerange(c2, V2(c1.x, c2.y))
        ):
            for pos in side:
                if roi is None or pos in roi:
                    yield pos

    def apply_roi(self, roi):
        c1 = V2(max(self.c1.x, roi.c1.x), max(self.c1.y, roi.c1.y))
        c2 = V2(min(self.c2.x, roi.c2.x), min(self.c2.y, roi.c2.y))
        return type(self)(c1, c2)


    @classmethod
    def layers(cls, starting: "V2", roi: "Rect"):
        """yields a series of growing rectangles centered on starting, until no
        border cell fits inside the roi
        """
        starting = V2(starting)

        side = 0
        while True:
            c1 = starting + side * V2(-1, -1)
            c2 = starting + side * V2(1, 1)
            c3 = (c2.x, c1.y)
            c4 = (c1.x, c2.y)
            if c1 not in roi and c2 not in roi and c3 not in roi and c4 not in roi:
                break
            yield cls(c1, c2)
            side += 1

    def shrink(self, n=1):
        return type(self)(self.c1 + n * (1,1), self.c2 + n * (-1,-1))

    def __repr__(self):
        return f"Rect({self.c1}, {self.c2})"

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


class SimpleWalker:
    def __init__(self, map, pos, last_pos=None, weight=0):
        self.pos = pos
        self.map = map
        self.last_pos = last_pos
        self.weight = weight

    def step(self):
        orig_pos = self.pos
        walkers = set()
        for direction in DIRECTIONS.values():
            target = orig_pos + direction
            if target == self.last_pos: continue
            if not self.map.inrange(target): continue
            if (cell:=self.map[target]).is_wall: continue
            next_weight = self.weight + 1
            if cell.weight is None or cell.weight > next_weight:
                new_walker = type(self)(self.map, target, self.pos, next_weight)
                cell.weight = next_weight
                walkers.add(new_walker)
        return walkers



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
        self.history = None

        self.inner_source = None

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
                self[x,y].inner_source = None

        self.generation = 0
        self.current_gen = []
        self.current_ids = {}

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
        print("\x1b[H", end="")
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                if (x,y) in getattr(self, "roi", {}):
                    line += "\x1b[45m"
                if self[x, y].is_wall:
                    line += "#####"
                elif self[x,y].weight is None:
                    line += "     "
                else:
                    weight = getattr(self[x,y], "long_weight", self[x,y].weight)
                    line += f"{weight:^5d}"
                if (x,y) in getattr(self, "roi", {}):
                    line += "\x1b[49m"
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

    def mark(self, pos, last_pos, weight, history):
        if (self[pos].weight or 0) < (weight or 0):
            self[pos].weight = weight
            self[pos].history = history
        #self[pos].last_pos = last_pos
        for direction in DIRECTIONS.values():
            target = pos + direction
            if not self.inrange(target) or (nc:=self[target]).is_wall:
                continue
            #if target == last_pos:
                #continue
            if target in history:
                continue
            self.current_gen.append((target, nc, pos, history))

    def advance_generation(self):
        self.next_gen = self.current_gen
        self.current_gen = []


    def lifegridsolver(self, print_=True):
        # tried to do it without the "walker" agents: no avail, it is
        # jut the same thing, but with tuples passed back and
        # forth instead of walker instances.

        self.reset()
        self.generation = 0
        weight = 0
        self.mark(self.starting_pos, None, weight, History(self.starting_pos))
        changed = True
        i = 0
        while changed:
            changed = False
            self.advance_generation()
            next_weight = weight + 1
            #if next_weight == 55:
                #breakpoint()
            target_weights = {}
            for pos, cell, last_pos, history in self.next_gen:
                if pos not in target_weights:
                    # this mini caching allows to pathes to cross-over.
                    target_weights[pos] = cell.weight or 0
                if cell.weight is None or target_weights[pos] < next_weight:
                    changed = True
                    self.mark(pos, last_pos, next_weight,  history + pos)
            i += 1
            if print_:
                self.print()
                time.sleep(0.1)
            elif not i%100:
                print ("\r", i, len(self.current_gen), end="   ", flush=True)
            weight = next_weight
        return self.result

    def reverse_first_solver(self, print_=False):
        self.reset()

        # (1) Annotate shorter paths to exit - normal dikstra stuff
        walkers = {SimpleWalker(self, self.ending_pos)}
        self[self.ending_pos].weight = 0
        while walkers:
            new_walkers = set()
            for walker in walkers:
                new_walkers.update(walker.step())
            walkers = new_walkers

        if print_:
            self.print()
        # 2 - from the beggining, follow a single path, taking _always_
        # the longer turn

        pos = self.starting_pos
        last_pos = None
        turn_stack = []
        weight = 1
        self[pos].long_weight = 0
        self[pos].visited = 1
        while True:
            self[pos].visited = True
            valid_paths = []
            for direction in DIRECTIONS.values():
                target = pos + direction
                if target == last_pos: continue
                if not self.inrange(target): continue
                if (cell:=self[target]).is_wall: continue
                if getattr(cell, "visited", False): continue
                valid_paths.append(target)

            if len(valid_paths) > 1:
                turn_stack.append(pos)
            elif len(valid_paths) == 0:
                if not turn_stack:
                    break
                pos = turn_stack.pop()
                weight = self[pos].long_weight
                last_pos = self[pos].last_pos
                continue
            last_pos = pos

            pos = max(valid_paths, key=lambda pos:self[pos].weight)
            self[pos].visited = 1
            self[pos].long_weight = weight
            self[pos].last_pos = last_pos
            weight += 1
            if print_:
                self.print()
                time.sleep(0.2)

        return self[self.ending_pos].long_weight

    def get_weight_from_neigbours(self, pos, roi, last_layer=frozenset()):
        #print(pos, last_layer)
        #if self[pos].weight == 19:
            #breakpoint()
        blank_inner = None
        inner_source = None
        neighbours = set()
        for delta in DIRECTIONS.values():
            target = pos + delta
            if target not in roi:
                continue
            cell = self[target]
            if cell.is_wall:
                continue
            cell = self[target]
            neighbours.add((cell, target))
            if target in last_layer:
                if cell.weight is None:
                    # an unvisited path in an inner layer has been found!
                    blank_inner = target
                else:
                    inner_source = target

        desired_neighbour = max(neighbours, key=lambda x: x[0].weight or -1)
        if desired_neighbour[1] != inner_source:
            inner_source = desired_neighbour[0].inner_source
        return desired_neighbour[0].weight, inner_source, blank_inner



    def reverse_layers(self, starting_pos=None, roi=None, last_layer=None, print_=True):
        """6th attempt for a solution for part2:
        we will draw concentric expanding rects around the exit, annotating the
        longest path as "weight" olong these rects as we exapand.

        recursive provisions should calculate any path-gains by inner loops
        with entrances that just show up on outer-concentric-rect layers.

        """
        if starting_pos is None:
            starting_pos = self.ending_pos
            roi = Rect(V2(0,0), V2(self.width - 1, self.height - 1))
            self.reset()

        layer_cells = {}
        for layer_num, layer in enumerate(Rect.layers(starting_pos, roi)):
            layer_cells[layer_num] = set()
            if layer_num == 0:
                pos = layer.c1
                if (w:=self.get_weight_from_neigbours(pos, roi)[0]) is None:
                    # we are just getting started!
                    #also a starting point, the "c1" in a zeroth layer
                    # must always be a walkable point!
                    # (either the maze exit or the entrance to an inner loop)
                    if self[pos].is_wall:
                        raise RuntimeError()
                    self[pos].weight = 0
                    self[pos].inner_source = 0
                else:
                    # we should just enter blank "starting pos"  -
                    # but just in case, let's take the max!
                    self[pos] = max(w + 1, self[pos].weight or 0)
                last_layer = set(layer.c1)
                continue

            changed = True
            blank_inners = {}

            while changed or blank_inners:
                if blank_inners and not changed:
                    new_roy = layer.shrink().apply_roi(roi)
                    # selects the inward entrance with the largest
                    # weight in a neighboring cell
                    blank_inner = max(
                        blank_inners.items(),
                        key=lambda item: item[1]
                    )[0]
                    self.reverse_layers(blank_inner, new_roy, layer_cells, print_)
                    changed = True
                    blank_inners = {}
                    continue

                changed = False
                for pos in layer.iter_wall(roi):
                    if self[pos].is_wall:
                        continue
                    layer_cells[layer_num].add(pos)
                    w, inner_source, blank_inner = self.get_weight_from_neigbours(pos, layer, last_layer)
                    if blank_inner:
                        #entrance to unvisited inner-loop (or dead end) found.
                        blank_inners[blank_inner] = (w or 0) + 1

                    if w is None:
                        continue
                        #raise RuntimeError()
                    new_weight = w + 1
                    # the "inner_source" means an inner-layer "source of truth" for the
                    # cell being updated - and is what avoids cells in the same
                    # layer to infinitelly augent one another.
                    # (without having to manually handle contiguous regions in the same layer)
                    if (self[pos].weight or 0) < new_weight and (self[pos].inner_source != inner_source):
                        changed = True
                        self[pos].weight = new_weight
                        self[pos].inner_source = inner_source
                if print_:
                    self.roi = layer
                    self.print()
                    time.sleep(0.1)
            last_layer = layer_cells.get(layer_num - 1, set())

        return self[self.starting_pos].weight
