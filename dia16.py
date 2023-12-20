from copy import deepcopy, copy


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
    def __hash__(self):
        return hash(tuple(self))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y})"



M1 = "/"
M2 = "\\"
SP1 = "|"
SP2 = "-"
EMPTY = "."
END = "$"

class Ray:
    def __init__(self, parent, position, direction):
        self.parent = parent
        self.history = [(position, direction)]
        self.direction = direction
        self.alive = True

    def split(self, new_direction):
        new_ray = (t:=type(self)).__new__(t)
        new_ray.history = copy(self.history)
        new_ray.direction = new_direction
        new_ray.parent = self.parent
        new_ray.alive = True
        return new_ray

    def step(self):
        op = self.parent[self.position]
        new_direction = dir = self.direction
        if op == M1: # /
            if dir == (1, 0):
                new_direction = V2(0, -1)
            elif dir == (-1, 0):
                new_direction = V2(0, 1)
            elif dir == (0, 1):
                new_direction = V2(-1, 0)
            elif dir == (0, -1):
                new_direction = V2(1, 0)
        elif op == M2: # \\
            if dir == (1, 0):
                new_direction = V2(0, 1)
            elif dir == (-1, 0):
                new_direction = V2(0, -1)
            elif dir == (0, 1):
                new_direction = V2(1, 0)
            elif dir == (0, -1):
                new_direction = V2(-1, 0)
        elif op == SP1: # |
            if dir in ((1, 0), (-1,0)):
                new_direction = V2(0, 1)
                self.parent.rays.append(self.split(V2(0, -1)))
                #print(len(self.parent.rays))
        elif op == SP2: # -
            if dir in ((0, 1), (0, -1)):
                new_direction = V2(1, 0)
                self.parent.rays.append(self.split(V2(-1, 0)))
        new_pos = self.position + new_direction
        ray_info = (new_pos, new_direction)
        if self.parent[new_pos] == END or ray_info in self.history:
            self.kill()
            return
        ener_hist = self.parent.energized.setdefault(new_pos, [])
        self.history.append(ray_info)
        self.direction = new_direction
        if ray_info in ener_hist:
            if self.alive:
                self.kill()
            return
        ener_hist.append(ray_info)


    def kill(self):
        self.alive = False
        self.parent.rays.remove(self)

    @property
    def position(self):
        return self.history[-1][0]

class Grid:
    def __init__(self, data:str):
        self.data = data.split("\n")
        self.width = len(self.data[0])
        self.height = len(self.data)
        self.reset()

    def reset(self):
        self.rays = []
        self.energized = {}

    def trace(self, ray=None):
        self.reset()
        if ray is None:
            ray = Ray(self, V2(-1,0), V2(1,0))
        self.rays = [ray]
        while self.rays:
            for ray in self.rays[:]:
                ray.step()
        return self.count()

    def trace_max(self):
        counts = []
        for row in range(self.height):
            counts.append(self.trace(Ray(self, V2(-1, row), V2(1,0))))
            counts.append(self.trace(Ray(self, V2(self.width, row), V2(-1,0))))
        for col in range(self.width):
            counts.append(self.trace(Ray(self, V2(col, -1), V2(0,1))))
            counts.append(self.trace(Ray(self, V2(col, self.height), V2(0, -1))))
        return max(counts)


    def count(self):
        # returns number of energized cells: answer to part 1
        return len(self.energized)

    def __getitem__(self, index):
        if not 0 <= index[0] < self.width or not 0 <= index[1] < self.height:
            return END
        return self.data[index[1]][index[0]]

    def __setitem__(self, index, value):
        x, y = index
        line = self.data[y]
        self.data[y] = self.data[y][0:x] + value + self.data[y][x + 1:]

    @property
    def enerview(self):
        new = deepcopy(self)
        for pos in self.energized:
            new[pos] = "#"
        return repr(new)

    def __repr__(self):
        return "\n".join(self.data)
