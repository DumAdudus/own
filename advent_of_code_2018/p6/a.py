#!/usr/bin/env python
from collections import Counter

X = 0
Y = 1
BOUNDARY = 10
BARRIER = 10000
CRITERION = 10000

coords = {}
safezone = []
index = 1
x_min = y_min = 10000
x_max = y_max = 0

with open('q') as f:
    for l in f.read().splitlines():
        coord = tuple([int(x) for x in l.split(', ')])
        coords[index] = coord
        index += 1

        x_min = min(x_min, coord[X])
        y_min = min(y_min, coord[Y])
        x_max = max(x_max, coord[X])
        y_max = max(y_max, coord[Y])

trans_min = min(x_min, y_min)
width = x_max - trans_min + 1 + (BOUNDARY * 2)
height = y_max - trans_min + 1 + (BOUNDARY * 2)

plate = [0] * width * height

boarder_idx = set([0])
for idx, coord in coords.items():
    trans_x = coord[X] - trans_min + BOUNDARY
    trans_y = coord[Y] - trans_min + BOUNDARY
    pos = width * trans_y + trans_x
    plate[pos] = idx + BARRIER

for y in range(0, height):
    for x in range(0, width):
        pos = width * y + x
        min_dist = BARRIER
        dist_sum = 0
        for idx, coord in coords.items():
            trans_x = coord[X] - trans_min + BOUNDARY
            trans_y = coord[Y] - trans_min + BOUNDARY
            dist = abs(trans_x - x) + abs(trans_y - y)
            dist_sum += dist
            if plate[pos] > BARRIER:
                continue
            if dist == min_dist:
                plate[pos] = 0
            elif dist < min_dist:
                min_dist = dist
                plate[pos] = idx
        if x >= BOUNDARY and x <= width - BOUNDARY and \
            y >= BOUNDARY and x <= height - BOUNDARY and \
                dist_sum < CRITERION:
            safezone.append(tuple([x, y]))


for x in range(0, width):
    boarder_idx.add(plate[x])
    boarder_idx.add(plate[x + (height - 1) * width])
for y in range(0, height):
    boarder_idx.add(plate[y * width])
    boarder_idx.add(plate[y * width + width - 1])

print x_min, x_max, y_min, y_max
area_count = Counter(plate)
#print area_count
for idx in boarder_idx:
    area_count.pop(idx)
max_idx = max(area_count, key=area_count.get)
#print area_count
print max_idx, area_count[max_idx] + 1, coords[max_idx]

print len(safezone)
