import re


class XMASProcessor:
    def __init__(self,  raw_data):
        self.load(raw_data)


    def load(self, raw_data):
        rules_str, parts_str = raw_data.split("\n\n")
        self.parts = [
            {key:int(num) for key, num in zip("xmas", re.findall(r"\d+", line))}
            for line in parts_str.split("\n")
        ]

        self.rules = dict(self.rule_factory(line) for line in rules_str.split("\n"))

    def rule_factory(self, rule_line):
        name, rules_str = rule_line.split("{")
        rules_str = rules_str.strip("}")
        rule_chain = "lambda part: "
        for rule_str in rules_str.split(","):
            if ":" not in rule_str:
                rule_chain += f' "{rule_str}"'
                break
            predicate, target = rule_str.split(":")

            rule_chain += f' "{target}" if part["{predicate[0]}"] {predicate[1:]} else '
        rule = eval(rule_chain)
        return name, rule

    def xunglepart(self, part):
        target = "in"
        while target not in "AR":
            target = self.rules[target](part)
        return target

    def mungleallz(self):
        return [
            part for part in self.parts
                if self.xunglepart(part) == "A"
        ]

    def doit(self):
        return sum(sum(part.values()) for part in self.mungleallz())



    def __repr__(self):
        return f"{self.__class__.__name__} <{repr(self.rules)[:300]!s}...>"

