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
            for  x in range(self.width):
                if self[x,y] == GALAXY:
                    yield(x,y)

    def __getitem__(self, pos):
        x, y = pos
        return self.data[y][x]

    def _expand_horizontal(self):
        rows_to_dup = []
        for i, row in enumerate(self.data):
            if all(item == SPACE for item in row):
                rows_to_dup.append(i)
        for index in reversed(rows_to_dup):
            self.data.insert(index + 1, self.data[index][:])

    def _expand_vertical(self):
        cols_to_dup = []
        for col in range(self.width):
            if all(self[col, row] == SPACE for row in range(self.height)):
                cols_to_dup.append(col)
        for index in reversed(cols_to_dup):
            self._dup_col(index)

    def _dup_col(self, index):
        for i, row in enumerate(self.data):
            # row is an str
            self.data[i] = row[:index] + row[index] + row[index:]

    def expand(self):
        self._expand_horizontal()
        self._expand_vertical()
    def __repr__(self):
        return "\n".join(self.data)


