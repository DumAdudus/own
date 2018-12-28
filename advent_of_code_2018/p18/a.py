#!/usr/bin/env python
import copy

area_init = list()
history = list()
ROUNDS = 1000000000
ROUNDS = 1000
ROUNDS = 580

OPEN = '.'
TREE = '|'
LUMBER = '#'

with open('q') as f:
    for line in f.read().splitlines():
        area_init.append(list(line))

width = height = len(area_init[0])
area_cur = copy.deepcopy(area_init)


def get_new_value(x, y):
    open_count = tree_count = lumber_count = 0
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            if (i, j) == (0, 0):
                continue
            nx = x + j
            ny = y + i
            if nx < 0 or ny < 0 or nx > width - 1 or ny > height - 1:
                continue
            if area_cur[ny][nx] == OPEN:
                open_count += 1
            elif area_cur[ny][nx] == TREE:
                tree_count += 1
            else:
                lumber_count += 1
    cur = area_cur[y][x]
    nv = cur
    if cur == OPEN:
        if tree_count >= 3:
            nv = TREE
    elif cur == TREE:
        if lumber_count >= 3:
            nv = LUMBER
    else:
        if not (lumber_count >= 1 and tree_count >= 1):
            nv = OPEN

    return nv


def print_area(r):
    print '\n' * 2 + str(r) +  '=' * 150
    for row in area_cur:
        print ''.join(row)

r = 0
while r < ROUNDS:
    y = 0
    history.append(area_cur)
    area_next = copy.deepcopy(area_cur)
    for row in area_cur:
        x = 0
        for col in row:
            nv = get_new_value(x, y)
            area_next[y][x] = nv
            x += 1
        y += 1
    area_cur = copy.deepcopy(area_next)
    try:
        i = history.index(area_next)
        print i, len(history)
    except ValueError:
        pass

    r += 1
    # if r > 200:
    #     print_area(r)

tree_sum = sum([x.count(TREE) for x in area_cur])
lumber_sum = sum([x.count(LUMBER) for x in area_cur])

print tree_sum * lumber_sum
