import re
from functools import cache
from collections import namedtuple

import pytest

# cache = lambda x:x

def parse_line(line):
    body, groups = line.split(" ")
    groups = tuple(int(g) for g in groups.split(","))
    return body, groups


#def check_line(body: str, groups):
    #if not groups and "#" in body: # or 1 in body):
        #return False, 0
    #groups_iter = iter(groups)
    #group_size = next(groups_iter)
    #cursor = 0
    #group_span = 0
    #inside_group = False
    #while cursor < len(body):
        #if body[cursor] == "#": # or body[cursor] == 1:
            #inside_group = True
            #group_span += 1
        #elif inside_group:  # elif body[cursor] == "."
            #inside_group = False
            #if group_span != group_size:
                #return False, cursor
            #group_size = next(groups_iter, None)
            #if group_size is None:
                #if "#" in (b:=body[cursor:]): # or 1 in b:
                    #return False, cursor
                #else:
                    #return True, cursor
            #group_span = 0
        #cursor += 1
    #if isinstance(group_size, int) and group_span != group_size:
        #return False, cursor
    #return not next(groups_iter, 0), cursor

#check_partial = namedtuple("check_partial", "works index next_groups force_dot")

@cache
def check_partial_line(body: str, groups: tuple) -> (bool, int, tuple, bool):
    # Verify if a line is valid for the given groups
    # up to the point the first "?" is met.
    # returns the index where checking failed,
    # and the remaining groups.
    # if returned groups is empty and index == len(body):
    # line is complete
    iter_groups = iter(groups)
    group_size = next(iter_groups, None)

    inside_group = False
    group_count = 0
    last_good_index = 0

    for i, char in enumerate(body):
        if group_size is None:
            break
        if char == "#":
            if not inside_group:
                last_good_index = i
                inside_group = True
                group_count = 0
            group_count += 1
        elif char == ".":
            if not inside_group:
                continue
            if group_size != group_count:
                # invalid match
                return False, last_good_index, (group_size, *iter_groups), None
            last_good_index = i
            inside_group = False
            group_size = next(iter_groups, None)
        else: # char == "?"
            if inside_group:
                if group_size == group_count:
                    # The 3rdy parameter as "True" means the current "?" is to be forced to "." when carrying on.
                    return None, i, tuple(iter_groups), "force_dot"
                elif group_size < group_count:
                    return False, last_good_index, (group_size, *iter_groups), None
                else: #elif group_size > group_count:
                    return None, last_good_index, (group_size, *iter_groups), "force_hash"
            return None, i, (group_size, *iter_groups), None


    if (
        group_size is None and "#" in body[i:] or
        group_size and "#" not in body[i:]
    ):
        return False, last_good_index, (group_size, *iter_groups), None
    elif inside_group:
        if group_size == group_count:
            remaining = tuple(iter_groups)
            if not remaining:
                return True, i + 1, tuple(iter_groups), None
            else:
                return False, i + 1, tuple(iter_groups), None
        return False, last_good_index, (group_size, *iter_groups), None
    remaining = tuple(iter_groups)
    return not remaining, i + 1, remaining, None

def check_line(body, groups):
    r = check_partial_line(body, groups)
    return r[0]

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

#def process_line(body, groups, prefix=""):
    #results = 0
    #if len(body) == 0 or "?" not in body:
        #return check_line(prefix + body, groups)
    #next_wild = body.find("?")
    #prefix = prefix + body[:next_wild]
    #body = body[next_wild + 1:]
    #count_f, failed_at = process_line("#" + body, groups, prefix)
    ##if count_f == 0 and failed_at < len(prefix) - 2:
        ##return 0, failed_at
    #count_o, failed_at_o = process_line("." + body, groups, prefix)
    #failed_at = min(failed_at, failed_at_o)
    #return count_f + count_o, failed_at

@cache
def process_line(body, groups: tuple):
    # print(body, groups)
    results = 0
    if len(body) == 0 or "?" not in body:
        return int( check_line(body, groups))
    valid, index, next_groups, force_next = check_partial_line(body, groups)
    match valid:
        case True:
            return 1
        case False:
            return 0
        case None:
            pass
        case _:
            raise RuntimeError()
    next_body = body[index:]
    next_wild = next_body.find("?")
    if next_wild == -1:
        return 1
    if force_next in (None, "force_dot"):
        results = process_line(next_body[:next_wild] + "." + next_body[next_wild + 1:], next_groups)
    else:
        results = 0

    if force_next in (None, "force_hash"):
        results += process_line(next_body[:next_wild] + "#" + next_body[next_wild + 1:], next_groups)
    return results




def process_all(data, collate=1, interval=25):
    lines = [parse_line(line) for line in data.split("\n")]
    if collate > 1:
        lines = [part2tize_line(*line, collate=collate) for line in lines]
    result = 0
    for i, line in enumerate(lines):
        result += (possibilities:=process_line(*line))
        # print (line, possibilities)
        if i % interval == 0:
            print(f"at line {i}: {possibilities}")
    return result






