from collections import deque
from itertools import cycle, tee
import math

aa = """LLR

AAA = (BBB, BBB)
BBB = (AAA, ZZZ)
ZZZ = (ZZZ, ZZZ)"""

def extract_data(data):
    directions_str, graph_str = data.split("\n\n")
    graph = {}
    for line in graph_str.split("\n"):
        key, targets = line.split(" = ")
        graph[key] = targets.strip("()").split(", ")
    return directions_str, graph

def walk(directions, graph):
    steps = 0
    node = "AAA"
    for i, direction in cycle(directions):
        steps += 1
        node = graph[node][direction == "R"]
        if node == "ZZZ":
            break
    return steps


class Walker:
    def __init__(self, graph, directions, start_node):
        self.graph = graph
        self.directions_str = directions
        self.start_node = start_node
        self.num_cycles = 1
        self.reset()
    def reset(self):
        self.node = self.start_node
        self.directions = cycle(enumerate(self.directions_str))
        self.steps = 0
        self.done = False
        self.started_directions = set()
        self.end_nodes = set()
        self.cycle_nodes = set()
        self.total_cycles = 0
    def __iter__(self):
        self.reset()
        for direction in self.directions:
            if self.steps and direction[0] == 0:
                if self.node in self.cycle_nodes:
                    self.cycle_size = self.steps
                    self.total_cycles += 1
                    if self.total_cycles >= self.num_cycles:
                        break
                    else:
                        self.cycle_nodes.clear()
                self.cycle_nodes.add(self.node)
            self.steps += 1
            self.node = self.graph[self.node][direction[1] == "R"]
            if self.node[-1] == "Z":
                self.end_nodes.add(self.steps)
                yield self.steps

def get_starting_nodes(graph):
    return [node for node in graph if node[-1] == "A"]

def do_it_part2(data):
     d, g = extract_data(data)
     walkers = [Walker(g, d, path) for path in get_starting_nodes(g)]
     # process everyone
     deque((deque(w, maxlen=0) for w in walkers), maxlen=0)
     # there is only one ending node per path in the input, so:
     ending_nodes = [w.end_nodes.pop() for w in walkers]
     # the answer is the least common multiple of
     # all ending nodes positions.
     # Python has it in the stdlib, otherwise
     # we'd face some extra 12 LoC
     return math.lcm(*ending_nodes)

