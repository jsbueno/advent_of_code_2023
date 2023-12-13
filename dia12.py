import re

import pytest


def parse_line(line):
    body, groups = line.split(" ")
    groups = [int(g) for g in groups.split(",")]
    return body, groups


def check_line(body: str, groups):
    if not groups and "#" in body: # or 1 in body):
        return False, 0
    groups_iter = iter(groups)
    group_size = next(groups_iter)
    cursor = 0
    group_span = 0
    inside_group = False
    while cursor < len(body):
        if body[cursor] == "#": # or body[cursor] == 1:
            inside_group = True
            group_span += 1
        elif inside_group:  # elif body[cursor] == "."
            inside_group = False
            if group_span != group_size:
                return False, cursor
            group_size = next(groups_iter, None)
            if group_size is None:
                if "#" in (b:=body[cursor:]): # or 1 in b:
                    return False, cursor
                else:
                    return True, cursor
            group_span = 0
        cursor += 1
    if isinstance(group_size, int) and group_span != group_size:
        return False, cursor
    return not next(groups_iter, 0), cursor
    #return True

def part2tize_line(line, groups, collate=5):
    line = "?".join([line,] * collate)
    groups *= collate
    return line, groups


#def process_line(body, groups):
    #wild_cards = body.count("?")
    #results = 0
    #for i in range(0, 2 ** wild_cards):
        #bit_string = iter(f"{i:0{wild_cards}b}")
        #fixed_body = [0 if c == "." else 1 if c == "#" else int(next(bit_string)) for c in body]
        #if checked:= check_line(fixed_body, groups):
            ## print(fixed_body, groups, checked)
            #results += 1#check_line(fixed_body, groups)
    #return results

def process_line(body, groups, prefix=""):
    results = 0
    if len(body) == 0 or "?" not in body:
        return check_line(prefix + body, groups)
    next_wild = body.find("?")
    prefix = prefix + body[:next_wild]
    body = body[next_wild + 1:]
    count_f, failed_at = process_line("#" + body, groups, prefix)
    #if count_f == 0 and failed_at < len(prefix) - 2:
        #return 0, failed_at
    count_o, failed_at_o = process_line("." + body, groups, prefix)
    failed_at = min(failed_at, failed_at_o)
    return count_f + count_o, failed_at



def process_all(data, collate=1):
    lines = [parse_line(line) for line in data.split("\n")]
    if collate > 1:
        lines = [part2tize_line(*line, collate=collate) for line in lines]
    result = 0
    for i, line in enumerate(lines):
        result += (possibilities:=process_line(*line)[0])
        # print (line, possibilities)
        if i % 1 == 0:
            print(f"at line {i}")
    return result






