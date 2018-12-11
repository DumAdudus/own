#!/usr/bin/env python
import math

SN = 18
SN = 42
SN = 9435
GRID_W = GRID_H = 300
SQUARE_SIZE = 3

power_grid = [0] * GRID_W * GRID_H


def hrd_digit(num):
    return int(math.floor(num / 100.0)) % 10


def print_sq(x, y, ss):
    global power_grid
    for i in range(0, ss):
        base_pos = (y + i) * GRID_W + x
        print power_grid[base_pos: base_pos + ss]
        print ' '.join([str(x) for x in power_grid[base_pos: base_pos + ss]])


def square_power(x, y, ss, left_sum=None):
    global power_grid
    psum = 0
    if x == 0 or not left_sum:
        for i in range(0, ss):
            base_pos = (y + i) * GRID_W + x
            psum += sum(power_grid[base_pos: base_pos + ss])
    else:
        psum = left_sum
        for i in range(0, ss):
            psum += power_grid[(y + i) * GRID_W + x + ss - 1] - power_grid[(y + i) * GRID_W + x - 1]

    return psum


for y in range(0, GRID_H):
    for x in range(0, GRID_W):
        rackid = (x + 1) + 10
        power_level = rackid * (y + 1)
        power_level += SN
        power_level *= rackid
        power_level = hrd_digit(power_level) - 5
        power_grid[x + y * GRID_W] = power_level

allsum = {}

for size in range(SQUARE_SIZE, GRID_W + 1):
    max_sum = -5 * size * size
    max_pos = ()
    for y in range(0, GRID_H - size + 1):
        left_sum = None
        for x in range(0, GRID_W - size + 1):
            s_power = square_power(x, y, size, left_sum)
            left_sum = s_power
            if s_power > max_sum:
                max_sum = s_power
                max_pos = (x, y)

    print [x + 1 for x in max_pos], max_sum, size
    allsum[max_pos] = (max_sum, size)

allmax = max(allsum, key=lambda k: allsum[k][0])
print allmax, allsum[allmax]

