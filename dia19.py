import re
from operator import lt, gt

RANGE_ALL = range(4000)

class Rule:
    def __init__(self, ruleset: dict, rule_line:str, rule_index=0):
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
        self.op = gt if predicate[1]==">" else lt
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

    def __repr__(self):
        return f"Rule {self.index} of {self.line}"


class XMASProcessor:
    def __init__(self,  raw_data):
        self.load(raw_data)


    def load(self, raw_data):
        rules_str, parts_str = raw_data.split("\n\n")
        self.parts = [
            {key:int(num) for key, num in zip("xmas", re.findall(r"\d+", line))}
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
        return [
            part for part in self.parts
                if self.xunglepart(part) == "A"
        ]

    def doit_part1(self):
        return sum(sum(part.values()) for part in self.mungleallz())

    doit = doit_part1

    def __repr__(self):
        return f"{self.__class__.__name__} <{len(self.rules)} rules>"

