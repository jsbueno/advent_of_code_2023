

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

    def __radd__(self, other):
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

    def manhattan(self, other):
        return abs(self[0] - other[0]) + abs(self[1] - other[1])


UP = V2(0,-1)
DOWN = V2(0, 1)
LEFT = V2(-1, 0)
RIGHT = V2(1, 0)


DIRECTIONS = {
    "U": UP,
    "R": RIGHT,
    "D": DOWN,
    "L": LEFT,
}

class Map:
    def __init__(self, data:str):
        self.load(data)

    def load(self, instructions):
        grid = dict()
        l_left = l_right = l_up = l_down = 0
        cursor = V2(0, 0)
        grid[cursor] = "#ffffff"
        count = 1
        for line in instructions.split("\n"):
            direction, length, color = line.split()
            direction = DIRECTIONS[direction]
            color = color.strip("()")
            for i in range(int(length)):
                cursor += direction
                grid[cursor] = color
                if cursor not in grid:
                    count += 1
            if cursor.x < l_left:
                l_left = cursor.x
            if cursor.x > l_right:
                l_right = cursor.x
            if cursor.y < l_up:
                l_up = cursor.y
            if cursor.y > l_down:
                l_down = cursor.y
        self.grid = grid
        self.topleft = V2(l_left, l_up)
        self.bottonright = V2(l_right, l_down) + V2(1,1)
        self.trenchlength = count

    @property
    def width(self):
        return self.bottonright.x - self.topleft.x

    @property
    def height(self):
        return self.bottonright.y - self.topleft.y

    def __getitem__(self, index):
        index += self.topleft
        return "#" if self.grid.get(index, None) else "."


    def __repr__(self):
        lines = []
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                line += self[x,y]
            lines.append(line)
        return "\n".join(lines)


