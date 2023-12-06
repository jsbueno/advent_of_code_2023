from copy import copy

def get_tables(data):
    all_tables = data.split("\n\n")
    return all_tables[0], all_tables[1:]

seeds, tables = get_tables(data)
seeds.removeprefix("seeds: ")
seeds = [int(seed) for seed in seeds.removeprefix("seeds: ").split()]


class Range:
    def __init__(self, text_range):
        dest, source, range_ = text_range.split(" ")
        self.dest_start = int(dest)
        self.source_start = int(source)
        self.range = int(range_)
        self.type_ = "source"

    def __contains__(self, number):
        """returns True if a number is contained in the source for this range"""
        return self.source_start <= number < self.source_start + self.range

    @property
    def destination(self):
        cpy = copy(self)
        cpy.source_start = self.dest_start
        cpy.type_ = "destination"
        return cpy

    def convert(self, number):
        return number - self.source_start + self.dest_start

    def __repr__(self):
        return f"{self.type_} Range source {self.source_start}, destination {self.dest_start}, range {self.range}"

class Table:
    table_index = {}
    def __init__(self, text_table):
        header, body = text_table.split("\n", 1)
        lines = body.split("\n")
        self.load_lines(lines)
        self.name = header.split()[0]
        self.source, _, self.destination = self.name.split("-")
        self.table_index[self.source] = self

    def load_lines(self, lines):
        self.ranges = [Range(line) for line in lines]

    def __getitem__(self, number):
        for r in self.ranges:
            if number in r:
                return r.convert(number)
        return number

    def __repr__(self):
        return f"Table {self.name} with {len(self.ranges)} ranges"

    @classmethod
    def get_final(self, initial_name, number):
        name = initial_name
        while table:=self.table_index.get(name, None):
            name = table.destination
            number = table[number]
        return number

# min(Tables.get_final("seed", seeds))
