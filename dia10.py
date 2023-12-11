
from functools import partial
import time

import pygame  # optional

#connection bits: 0b1000 is north, and the others follow
# clockwise up to 0b0001 for West

N, E, S, W = 0b1000, 0b0100, 0b0010, 0b0001

connect_map = {
    "|": 0b1010,
    "-": 0b0101,
    "L": 0b1100,
    "J": 0b1001,
    "7": 0b0011,
    "F": 0b0110,
    ".": 0b0000,
}
reverse_connect = {v: k for k, v in connect_map.items()}


class Maze:
    def __init__(self, data):
        self.data = data.split("\n")
        self.width = len(self.data[0])
        self.height = len(self.data)
        self.colors = {}
        self.find_start_pos()

    def __repr__(self):
        return "\n".join(self.data)

    def __getitem__(self, pos):
        x, y = pos
        if x < 0 or y < 0 or x >=self.width or y >= self.height:
            return "."
        return self.data[pos[1]][pos[0]]

    def directions(self, pos):
        char = self[pos]
        return connect_map[char]

    def mark_starting_pos(self, pos):
        if self[pos] != "S":
            raise ValueError()
        self.starting_pos = pos
        x, y = pos
        connected_sides = 0
        if self.directions((x, y-1)) & S:
            connected_sides |= N
        if self.directions((x + 1, y)) & W:
            connected_sides |= E
        if self.directions((x, y + 1)) & N:
            connected_sides |= S
        if self.directions((x - 1, y)) & E:
            connected_sides |= W
        starting_char = reverse_connect[connected_sides]
        line = list(self.data[y])
        line[x] = starting_char
        self.data[y] = "".join(line)
        self.colors[pos] = (0, 255, 0)

    def iterpos(self):
        for x in range(0, self.width):
            for y in range(0, self.height):
                yield (x,y)


    def find_start_pos(self):
        for x, y in self.iterpos():
            if self[x, y] == "S":
                self.mark_starting_pos((x, y))
                return
        raise ValueError("No starting position")

    def render(self, screen: "pygame.Surface", bgcolor=(0,0,0), color=(255,255,255)):
        pw, ph = screen.get_size()
        xstep = pw // (self.width + 1)
        ystep = ph // (self.height + 1)
        screen.fill(bgcolor)
        linew = max(int(xstep / 10), 1)
        # pos, x, y are nonlocal in "dl":
        F = 0.5
        dl = lambda ep: pygame.draw.line(
            screen,
            self.colors.get(pos, color),
            ((x + 1) * xstep, (y + 1) * ystep),
            (int((x + ep[0] * F + 1) * xstep), int((y + ep[1] * F + 1) * ystep)),
            width=linew
        )
        for x, y in self.iterpos():
            pos = x, y
            directions = self.directions(pos)
            if directions & N: dl((0, -1))
            if directions & E: dl((1, 0))
            if directions & S: dl((0, 1))
            if directions & W: dl((-1, 0))
        pygame.display.update()

    def walk(self, screen=None, delay=0.2, render_cycle=1):
        visited = {}
        paths = [(self.starting_pos, 0),]
        tick = 0
        while paths:
            new_paths = []
            for path in paths:
                pos, distance = path
                if pos not in visited or visited[pos] > distance:
                    visited[pos] = distance
                    self.colors.setdefault(pos, (0, 255, 255))
                    directions = self.directions(pos)
                    x, y = pos
                    if directions & N:                                new_paths.append(((x, y - 1), distance + 1))
                    if directions & E:                                new_paths.append(((x + 1, y), distance + 1))
                    if directions & S:                                new_paths.append(((x, y + 1), distance + 1))
                    if directions & W:                                new_paths.append(((x - 1, y), distance + 1))
            if screen:
                tick += 1
                if tick % render_cycle == 0:
                    self.render(screen)
                    time.sleep(delay)
            paths = new_paths
        return max(visited.values())


