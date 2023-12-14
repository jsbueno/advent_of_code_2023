from copy import copy
from itertools import dropwhile


class Indexable:
    def __init__(self, func):
        self.func = func
    def __repr__(self):
        return "Instancia de Indexable"

    def __get__(self, instance, owner=None):
        indexable = copy(self)
        indexable.instance = instance
        return indexable

    def __getitem__(self, index):
        return self.func(self.instance, index)


class Map:
    needed_difference = 0

    def __init__(self, data: str):
        self.data = data.split("\n")
        self.width = len(self.data[0])
        self.height = len(self.data)

    def __getitem__(self, index):
        x, y = index
        return self.data[y][x]

    def equals(self, first, second):
        return (first == second), 0

    @Indexable
    def rows(self, index):
        return self.data[index]

    @Indexable
    def cols(self, index):
        return "".join(row[index] for row in self.data)

    def check_reflection(self, index, sequence):
        had_run = False
        smudges = 0
        for i, (j, forward_row) in zip(
            range(index, -1, -1),
            dropwhile(lambda pair: pair[0] <= index, enumerate(sequence))
        ):
            had_run = True
            backward_row = sequence[i]
            if not (comparison:=self.equals(forward_row, backward_row))[0]:
                return False
            smudges += comparison[1]
        if smudges != self.needed_difference:
            return False
        return had_run


    def find_reflection(self):
        prev = ""
        for i, row in enumerate(self.rows):
            if self.equals(row, prev)[0]:
                if self.check_reflection(i - 1, self.rows):
                    return i * 100
            prev = row
        prev = ""
        for i, col in enumerate(self.cols):
            if self.equals(col, prev)[0]:
                if self.check_reflection(i - 1, self.cols):
                    return i
            prev = col
        raise RuntimeError("Map without a reflection line")

    def  __repr__(self):
        return "\n".join(self.data)


class MapPart2(Map):

    needed_difference = 1

    def equals(self, first, second):
        if first == second:
            return True, 0
        differences = sum(c1 != c2 for c1, c2 in zip(first, second))
        if differences <= self.needed_difference:
            return True, differences
        return False, 0

def do_it_part1(data):
    return sum(Map(map).find_reflection() for map in data.split("\n\n"))

def do_it_part2(data):
    return sum(MapPart2(map).find_reflection() for map in data.split("\n\n"))
