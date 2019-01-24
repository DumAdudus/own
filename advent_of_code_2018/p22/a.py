#!/usr/bin/env python
import enum


ERO_MODULO = 20183
TYPE_MODULO = 3
Y_MUL = 16807
X_MUL = 48271

cave_depth = 4848
coord_tgt = (15, 700)

cave_depth = 510
coord_tgt = (10, 10)

EXPAND = 1 + 10
MAX_DIST = 100000000
cave_width = coord_tgt[0] + EXPAND
cave_height = coord_tgt[1] + EXPAND
cave = [['.' for x in range(cave_width)] for y in range(cave_height)]
cave_level = [[-1 for x in range(cave_width)] for y in range(cave_height)]


class Tool(enum.Enum):
    TORCH = 0
    GEAR = 1
    HAND = 2

class Spot(object):
    def __init__(self, pos, dist=MAX_DIST, tool=None):
        self.pos = pos
        self.dist = dist
        self.tool = tool

region_tools = {
    '.': [Tool.TORCH, Tool.GEAR],
    '=': [Tool.HAND, Tool.GEAR],
    '|': [Tool.TORCH, Tool.HAND]
}


cave_dist = [[Spot((0, 0)) for x in range(cave_width)] for y in range(cave_height)]
dist_queue = [Spot((0, 0), 0, Tool.TORCH)]


def calc_neighbor(spot):
    global cave_dist
    x, y = spot.pos
    # up
    nx = x
    ny = y - 1
    if ny > 0:


hit = 0
# @profile
def calc_index(coord):
    global hit
    x, y = coord
    if coord in [(0, 0), coord_tgt]:
        idx = 0
    elif y == 0:
        idx = x * Y_MUL
    elif x == 0:
        idx = y * X_MUL
    else:
        idx = calc_level((x - 1, y)) * calc_level((x, y - 1))
    hit += 1
    return idx

# @profile
def calc_level(coord):
    global cave_level
    x, y = coord
    lvl = cave_level[y][x]
    if lvl == -1:
        idx = calc_index(coord)
        lvl = (idx + cave_depth) % ERO_MODULO
        cave_level[y][x] = lvl
    return lvl

# @profile
def get_type(coord):
    lvl = calc_level(coord)
    typ = '.'
    if lvl % TYPE_MODULO == 1:
        typ = '='
    elif lvl % TYPE_MODULO == 2:
        typ = '|'
    return typ


riskmap = {'M': 0, 'T': 0, '.': 0, '=': 1, '|': 2}

# @profile
def calc_risk():
    risk = 0
    for row in cave:
        for c in row:
            risk += riskmap[c]
    return risk


def print_cave():
    for row in cave:
        print ''.join(row)


# @profile
def main():
    global cave
    for x in range(cave_width):
        cave[0][x] = get_type((x, 0))
        cave_dist[0][x].pos = (x, 0)
    for y in range(cave_height):
        cave[y][0] = get_type((0, y))
        cave_dist[y][0].pos = (0, y)

    for y in range(1, cave_height):
        # print hit
        # print ''.join(cave[y]), hit
        for x in range(1, cave_width):
            cave[y][x] = get_type((x, y))
            cave_dist[y][x].pos = (x, y)

    cave[0][0] = 'M'
    cave[coord_tgt[1]][coord_tgt[0]] = 'T'
    print_cave()
    print calc_risk()
    # print hit

main()



