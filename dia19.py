import re
from operator import lt, gt, le, ge
import math
import sys

sys.setrecursionlimit(5000)  # there are 1703 rules in my input.

INITIAL_RANGES = {k: [range(1, 4001)] for k in "xmas"}


class Rule:
    def __init__(self, ruleset: dict, rule_line: str, rule_index=0):
        self.ruleset = ruleset
        self.line = rule_line
        self.name, rules_str = rule_line.split("{")
        self.index = rule_index
        rule_str = rules_str.strip("}").split(",")[rule_index]
        if ":" not in rule_str:
            self.target = rule_str
            self.type = "final"
            self.register()
            return
        self.type = "cmp"
        predicate, self.target = rule_str.split(":")
        self.key = predicate[0]
        self.op = gt if predicate[1] == ">" else lt
        self.threshold = int(predicate[2:])
        self.register()
        type(self)(ruleset, rule_line, rule_index + 1)

    def register(self):
        self.ruleset[self.name, self.index] = self

    def __call__(self, part):
        if self.type == "final":
            return (self.target, 0)
        if self.op(part[self.key], self.threshold):
            return (self.target, 0)
        return self.name, self.index + 1

    @staticmethod
    def _ranges_to_possibilities(ranges):
        #print(ranges, end="")
        total = 1
        for key in "xmas":
            total_letter = 0
            for rng in ranges[key]:
                total_letter += len(rng)
            total *= total_letter
        #print(" total:", total)
        return total

    def calc_possibilities(self, ranges):
        if self.type == "final":
            return (
                0
                if self.target == "R"
                else self._ranges_to_possibilities(ranges)
                if self.target == "A"
                else self.ruleset[self.target, 0].calc_possibilities(ranges)
            )

        ranges_pass, ranges_fail = self.break_ranges(ranges)

        part1 = (
            self.ruleset[self.target, 0].calc_possibilities(ranges_pass)
            if self.target not in "AR"
            else self._ranges_to_possibilities(ranges_pass)
            if self.target == "A"
            else 0
        )
        part2 = self.ruleset[self.name, self.index + 1].calc_possibilities(ranges_fail)
        return part1 + part2

    def break_ranges(self, ranges):
        new_pass = []
        new_fail = []
        for rng in ranges[self.key]:
            if self.threshold not in rng:
                new_pass.append(rng)
                new_fail.append(rng)
                continue
            if self.op is lt:
                new_pass.append(range(rng.start, self.threshold))
                new_fail.append(range(self.threshold, rng.stop))
            else:
                new_fail.append(range(rng.start, self.threshold + 1))
                new_pass.append(range(self.threshold + 1, rng.stop))

        ranges_pass = ranges.copy()
        ranges_pass[self.key] = new_pass
        ranges_fail = ranges.copy()
        ranges_fail[self.key] = new_fail
        return ranges_pass, ranges_fail

    def __repr__(self):
        return f"Rule {self.index} of {self.line}"


class XMASProcessor:
    def __init__(self, raw_data):
        self.load(raw_data)

    def load(self, raw_data):
        rules_str, parts_str = raw_data.split("\n\n")
        self.parts = [
            {key: int(num) for key, num in zip("xmas", re.findall(r"\d+", line))}
            for line in parts_str.split("\n")
        ]

        self.rules = {}
        for line in rules_str.split("\n"):
            Rule(self.rules, line)

    def xunglepart(self, part):
        target = "in", 0
        while target[0] not in "AR":
            target = self.rules[target](part)
        return target[0]

    def mungleallz(self):
        return [part for part in self.parts if self.xunglepart(part) == "A"]

    def doit_part1(self):
        return sum(sum(part.values()) for part in self.mungleallz())

    doit = doit_part1

    def doit_part2(self):
        return self.rules["in", 0].calc_possibilities(INITIAL_RANGES)

    def __repr__(self):
        return f"{self.__class__.__name__} <{len(self.rules)} rules>"
