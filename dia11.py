from itertools import combinations

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
    def __init__(self, data: str, expansion=2):
        self.expansion = expansion - 1
        self.data = data.split("\n")
        self.expanded = False
        self.expand()
        self.expanded = True

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
        self._inner_expand_lines(lines_to_dup, direction)

    def _inner_expand_lines(self, lines_to_dup, direction):
        for index in reversed(lines_to_dup):
            for _ in range(self.expansion):
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

    @staticmethod
    def distance(pos1, pos2):
        return abs(pos2[0] - pos1[0]) + abs(pos2[1] - pos1[1])

    def doit(self):
        return sum(self.distance(*pair) for pair in combinations(self, 2))

    def __repr__(self):
        return "\n".join(self.data)


class MapaParte2(Mapa):
    """
    ATTENTION: there is an _ultimate_  "off by one" error lying around
    when the puzzle says "10 times larger" we are actually insrting
    _9_ new columns, not 10!

    """

    # This implementation keeps the original "data" ingested
    # without adding any "physical" dots as SPACE

    @property
    def width(self):
        if not self.expanded:
            return super().width
        return self.coord_to_expanded((len(self.data[0]), 0))[0]

    @property
    def height(self):
        if not self.expanded:
            return super().height
        return self.coord_to_expanded((0, len(self.data)))[1]

    def __iter__(self):
        for y in range(super().height):
            for x in range(super().width):
                if self[x,y] == GALAXY:
                    yield self.coord_to_expanded((x,y))

    def _inner_expand_lines(self, lines_to_dup, direction):
        setattr(self, f"{direction}_expansion", lines_to_dup[:])

    def __getitem__(self, pos):
        x, y = pos
        return self.data[y][x]

    # TODO: use a reverse "expansion" for a getitem that would work on
    # the expanded universe

    def coord_to_expanded(self, pos):
        new_coord = []
        for expansion_map, component in zip((self.vertical_expansion, self.horizontal_expansion), pos):
            new_comp = (len([c for c in expansion_map if c < component])  * self.expansion) + component
            new_coord.append(new_comp)
        return tuple(new_coord)

