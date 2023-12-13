import re

import pytest


def parse_line(line):
    body, groups = line.split(" ")
    groups = [int(g) for g in groups.split(",")]
    return body, groups

class CantFit(Exception):
    ...

class CantFeed(Exception):
    # When there are # groups that can't be fed
    # by the remaining groups.
    ...

#def assert_min_groups_hashes(body, groups):
    #hash_groups = re.findall(r"\#+", body)
    #if len(groups) < len(hash_groups):
        ## TBD test for ambiguous groups like "#?#"
        #raise CantFeed()
    #for group, hash_group in zip(groups, hash_groups):
        #if group != len(hash_group):
            ## TBD
            #raise CantFeed()
    #return True

def assert_min_groups_hashes(body, groups):
    cursor = 0
    groups = iter(groups)
    while cursor < len(body):
        group = next(groups, None)
        if not group and any(c == "#" for c in body[cursor:]):
            raise CantFeed()
        while len(body) > cursor and body[cursor] != "#":
            cursor += 1
        if cursor >= len(body):
            break
        if not (match:=re.match(rf"[#?]{{{group}}}", body[cursor:])):
            raise CantFeed()
        cursor += group + 1




def process_line(body, groups):
    if not groups:
        if "#" in body:
            raise CantFeed()
        return 1
    assert_min_groups_hashes(body, groups)
    minimal_group_size = sum(groups) + len(groups) - 1
    if minimal_group_size > len(body):
        raise CantFit()
    head, *tail = groups
    arranges = 0
    # head_arranges = []
    cursor = 0
    while minimal_group_size - cursor <= len(body):
        remaining = len(body[cursor:])
        if remaining < head:
            break
        if all(c in "#?" for c in body[cursor: cursor + head]) and (remaining == head or body[cursor + head] in "?."):
            # TBD filter for cases where the current group _must_ be ahead due to explicit "##"sequences
            ...
            try:
                arranges += process_line(body[cursor + head + 1:], tail)
            except CantFeed:
                cursor += 1
                continue
            except CantFit:
                break
        if body[cursor] == "#":
            break
        cursor += 1
    if arranges == 0:
        raise RuntimeError("Algo de Errado Não Está Certo")
    return arranges

@pytest.mark.parametrize(
    ("line", "expected"),[
        ("?###???????? 3,2,1", 10),
        ("??????? 2,1", 10),
        ("?###? 3", 1),
        ("????## 2", 1),
        ("????#?# 1,1", 1),
        ("????#?# 3", 1),
    ]
)
def test_process_line(line, expected):
    body, groups = parse_line(line)
    assert process_line(body, groups) == expected


