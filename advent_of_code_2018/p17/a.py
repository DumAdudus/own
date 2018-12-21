#!/usr/bin/env python
import re
import bisect
import signal
from collections import defaultdict


COORDS_PATTERN = '\w=(.+), \w=(.+)'
raw_clays = dict()
clays = dict()

axis_x = defaultdict(list)
axis_y = defaultdict(list)

min_x = min_y = 100000
max_x = max_y = 0

with open('q') as f:
# with open('example') as f:
    for line in f.read().splitlines():
        m = re.match(COORDS_PATTERN, line)
        if line.startswith('x'):
            x = int(m.group(1))
            up = int(m.group(2).split('..')[0])
            down = int(m.group(2).split('..')[1])
            min_x = min(x, min_x)
            max_x = max(x, max_x)
            min_y = min(up, min_y)
            max_y = max(down, max_y)
            for y in range(up, down + 1):
                raw_clays[(x, y)] = 1
        else:
            y = int(m.group(1))
            left = int(m.group(2).split('..')[0])
            right = int(m.group(2).split('..')[1])
            min_x = min(left, min_x)
            max_x = max(right, max_x)
            min_y = min(y, min_y)
            max_y = max(y, max_y)
            for x in range(left, right + 1):
                raw_clays[(x, y)] = 1


print min_x, max_x
print min_y, max_y

trans_x = min_x - 1
map_w = max_x - trans_x + 2
map_h = max_y + 1
ground = [['.'] * map_w for i in range(map_h)]


def show_ground():
    for l in ground:
        print ''.join(l)


spring = (500 - trans_x, 0)

ground[0][spring[0]] = '+'
for coord in raw_clays:
    x, y = coord
    nx = x - trans_x
    clays[(nx, y)] = 1
    axis_x[nx].append(y)
    axis_y[y].append(nx)
    ground[y][nx] = '#'

for k in axis_x:
    axis_x[k].sort()

for k in axis_y:
    axis_y[k].sort()


def find_boarder(x, y):
    pos = bisect.bisect(axis_y[y], x)
    if pos == 0:
        left = -2
    else:
        left = axis_y[y][pos - 1]
    if pos == len(axis_y[y]):
        right = map_w + 100
    else:
        right = axis_y[y][pos]
    return left, right


def reach_bottom(x, y):
    if y + 1 == map_h:
        return False
    down = y + 1
    return ground[down][x] in '#~'


def bottom_range(x, y):
    down = y + 1
    left = x
    right = x
    while left >= 0:
        left -= 1
        if ground[down][left] not in '#~':
            left += 1
            break
    while right < map_w:
        right += 1
        if ground[down][right] not in '#~':
            right -= 1
            break
    return left, right


cur_drop = (spring[0], spring[1])
cur_pos = (spring[0], spring[1] + 1)
drop_point = list()
drop_point_history = dict()


def add_drop(x, y):
    if (x, y) not in drop_point_history:
        drop_point.append((x, y))
        drop_point_history[(x, y)] = 1

try:
    while True:
        if not cur_drop:
            cur_drop = drop_point.pop(0)
            x = cur_drop[0]
            y = cur_drop[1] + 1
        else:
            x, y = cur_pos
        if ground[y][x] != '#':
            if reach_bottom(x, y):
                left, right = find_boarder(x, y)
                bottom_left, bottom_right = bottom_range(x, y)
                if bottom_left <= left + 1:
                    if right - 1 <= bottom_right:       # hit both walls
                        ground[y][left + 1: right] = '~' * (right - left - 1)
                        cur_pos = (x, y - 1)
                    else:                               # hit left wall
                        ground[y][left + 1: bottom_right + 2] = '|' * (bottom_right - left + 1)
                        add_drop(bottom_right + 1, y)
                        cur_drop = None
                else:
                    if right - 1 <= bottom_right:       # hit right wall
                        ground[y][bottom_left - 1: right] = '|' * (right - bottom_left + 1)
                        add_drop(bottom_left - 1, y)
                        cur_drop = None
                    else:                               # hit no walls
                        ground[y][bottom_left - 1: bottom_right + 2] = '|' * (bottom_right - bottom_left + 3)
                        add_drop(bottom_left - 1, y)
                        add_drop(bottom_right + 1, y)
                        cur_drop = None
            else:
                ground[y][x] = '|'
                if y + 1 == map_h:      # reach end
                    if len(drop_point) > 0:
                        cur_drop = None
                    else:
                        break
                cur_pos = (x, y + 1)
        else:
            pass
except KeyboardInterrupt:
    pass

water = 0
for line in ground:
    water += line.count('|') + line.count('~')
print water
show_ground()




