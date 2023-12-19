from collections import deque

consume = lambda x: deque(x, maxlen=0)

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

    def __eq__(self, other):
        return self[0] == other[0] and self[1] == other[1]
    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y})"


BOULDER = "O"
COLUMN = "#"
SPACE = "."


NORTH = V2(0, -1)
WEST = V2(-1, 0)
SOUTH = V2(0, 1)
EAST = V2(1, 0)

class Map:
    gravity = NORTH
    def __init__(self, data:str):
        self.load(data)
    def load(self, data):
        self.data = [list(line) for line in data.split("\n")]
        self.width = len(self.data[0])
        self.height = len(self.data)
    def __getitem__(self, pos):
        if pos[0] < 0 or pos[1] < 0:
            raise IndexError()
        return self.data[pos[1]][pos[0]]
    def __setitem__(self, pos, val):
        self.data[pos[1]][pos[0]] = val


    def iter_pos(self):

        # Turns out match/case is even more useless than it appears
        # at first, as it would require workarounds to work here:
        if self.gravity == NORTH:
            outer_range = range(self.height)
            inner_range = range(self.width)
            axis = 0
        elif self.gravity == WEST:
            outer_range = range(self.width)
            inner_range = range(self.height)
            axis = 1
        elif self.gravity == SOUTH:
            outer_range = range(self.height - 1, -1, -1)
            inner_range = range(self.width)
            axis = 0
        elif self.gravity == EAST:
            outer_range = range(self.width - 1, -1, -1)
            inner_range = range(self.height)
            axis = 1

        self.lower_row = True
        #print(self.gravity)
        for i in outer_range:
            for j in inner_range:
                z=V2((j, i) if not axis else (i, j))
                #print(z, end=" ")
                yield z
            #print("end of lower row")
            #print()
            self.lower_row = False

    @property
    def lower_row(self):
        return self._lower_row
    @lower_row.setter
    def lower_row(self, val):
        #print("Changing lower_row to ", val)
        self._lower_row = val

    def move(self, pos1, pos2):
        self[pos2] = self[pos1]
        self[pos1] = SPACE

    def iter_once(self):
        self.stable = True
        for pos in self.iter_pos():
            if self[pos] == BOULDER:
                if self.lower_row:
                    continue
                elif self[pos + self.gravity] == SPACE:
                    self.move(pos, pos + self.gravity)
                    self.stable = False

    def __iter__(self):
        self.stable = False
        while not self.stable:
            yield self.eval()
            self.iter_once()

    def eval(self):
        load = 0
        for pos in self.iter_pos():
            if self[pos] == BOULDER:
                load += (self.height - pos.y)
        return load

    def cycle(self):
        for gravity in NORTH, WEST, SOUTH, EAST:
            self.gravity = gravity
            consume(self)
        return self.eval()

    def part2_iter(self):
        current = hash(self)
        i = 0
        all_states = set()
        while True:
            self.cycle()
            new_state = hash(self)
            if new_state == current:
                break
            current = new_state
            if current in all_states:
                raise RuntimeError(f"Repeated non consecutive state: {current}")
            all_states.add(current)
            i += 1
            if i %10 == 0:
                print(i)
        return current


    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return "\n".join("".join(char for char in line) for line in self.data)
