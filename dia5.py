from copy import copy

def get_tables(data):
    all_tables = data.split("\n\n")
    return all_tables[0], all_tables[1:]



class Range:
    def __init__(self, text_range):
        dest, source, range_ = text_range.split(" ")
        self.dest_start = int(dest)
        self.source_start = int(source)
        self.range = int(range_)
        self.type_ = "source"

    @property
    def source_end(self):
        return self.source_start + self.range
    @property
    def dest_end(self):
        return self.dest_start + self.range

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

    def key(self):
        return (self.source_start, self.range)

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
        self.ranges.sort(key=lambda r: r.key())

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

    def get_ranges_in_next_table(self, ranges:list[range]):
        result_ranges = []

        for source_range in ranges:
            start = source_range.start
            end = source_range.stop
            for comp_range in self.ranges:
                if start >= end:
                    break
                if (end < comp_range.source_start
                    or
                    start >= comp_range.source_end
                ):
                    continue
                # tem 3 casos agora: ou a faixa de sementes
                # 1) comeca antes e termina dentro da faixa comparada
                # 2) comeca dentro e termina dentro
                # 3) comeca dentro e termina fora da faixa comparada
                # 4) faixa comparada contida na faixa de sementes
                # caso 1:
                if start < comp_range.source_start and end < comp_range.source_end:
                    first_part = range(start, comp_range.source_start)
                    second_part = range(comp_range.source_start, end)
                    result_ranges.append(first_part)
                    mapped_second = range(comp_range.convert(second_part.start), comp_range.convert(second_part.end))
                    result_ranges.append(mapped_second)
                    break
                elif comp_range.source_start <= start and end < comp_range.source_end:
                    mapped_range = range(comp_range.convert(start), comp_range.convert(end))
                    result_ranges.append(mapped_range)
                    break
                elif comp_range.source_start <= start and comp_range.source_end <= end:
                    mapped_first = range(comp_range.convert(start), comp_range.convert(comp_range.source_end))
                    result_ranges.append(mapped_first)
                    start = comp_range.source_end

                else:
                    # caso 4: comp_range contida em seed_range
                    first_part = range(start, comp_range.source_start)
                    result_ranges.append(first_part)
                    second_part = range(comp_range.dest_start, comp_range.dest_end)
                    result_ranges.append(second_part)
                    #third_part = range(comp_range.source_end, end)
                    start = comp_range.source_end
            else:
                result_ranges.append(range(start, end))
        return result_ranges


seeds, tables = get_tables(data)
seeds.removeprefix("seeds: ")
seeds = [int(seed) for seed in seeds.removeprefix("seeds: ").split()]

live_tables = [Table(table) for table in tables]

# min(Tables.get_final("seed", seeds))
