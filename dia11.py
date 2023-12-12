class indexable:
    def __init__(self, func):
        self.func = func
    def __getitem__(self, index):

        return self.func(index)

GALAXY = "#"
SPACE = "."

aa = """...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#....."""

class Mapa:
    def __init__(self, data: str):
        self.data = data.split("\n")

    @property
    def width(self):
        return len(self.data[0])

    @property
    def height(self):
        return len(self.data)

    def __iter__(self):
        for y in range(self.height):
            for x in range(self.width):
                if self[x,y] == GALAXY:
                    yield(x,y)

    def __getitem__(self, pos):
        x, y = pos
        return self.data[y][x]

    def _expand_lines(self, direction="horizontal"):
        lines_to_dup = []
        outter_limit = self.width if direction == "vertical" else self.height
        inner_limit = self.height if direction == "vertical" else self.width
        for i in range(outter_limit):
            if all(self[(i, j) if direction=="vertical" else (j, i)] == SPACE for j in range(inner_limit)):
                lines_to_dup.append(i)
        for index in reversed(lines_to_dup):
            if direction == "vertical":
                self._dup_col(index)
            else:
                self.data.insert(index + 1, self.data[index][:])

    def _dup_col(self, index):
        for i, row in enumerate(self.data):
            # row is an str
            self.data[i] = row[:index] + row[index] + row[index:]

    def expand(self):
        self._expand_lines("horizontal")
        self._expand_lines("vertical")
    def __repr__(self):
        return "\n".join(self.data)


