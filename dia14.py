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
    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y})"


BOULDER = "O"
COLUMN = "#"
SPACE = "."


class Map:
    gravity = V2((0, -1))
    def __init__(self, data:str):
        self.load(data)
    def load(self, data):
        self.data = [list(line) for line in data.split("\n")]
        self.width = len(self.data[0])
        self.height = len(self.data)
    def __getitem__(self, pos):
        return self.data[pos[1]][pos[0]]
    def __setitem__(self, pos, val):
        self.data[pos[1]][pos[0]] = val


    def iter_pos(self):
        # FIXME: the correct iteration order
        # for movement evaluation depends
        # on tilt direction (self.gravity)
        # this is hardcoded to comply with (-1, 0)
        for y in range(self.height):
            for x in range(self.width):
                yield V2(x, y)

    def move(self, pos1, pos2):
        self[pos2] = self[pos1]
        self[pos1] = SPACE

    def iter_once(self):
        self.stable = True
        for pos in self.iter_pos():
            if self[pos] == BOULDER:
                if pos.y == 0:
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

    def __repr__(self):
        return "\n".join("".join(char for char in line) for line in self.data)
