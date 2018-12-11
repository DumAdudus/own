#!/usr/bin/env python
import copy
import re


PATTERN = r'.+<\s?([0-9-]+),\s+([0-9-]+)>.+<\s?([0-9-]+),\s+([0-9-]+)>'
P_IDX = 0
V_IDX = 1
X_IDX = 0
Y_IDX = 1
MAX_RANGE = 100
MAX_SEC = 15000
#MAX_SEC = 5

with open('q') as f:
    raw_info = f.read().splitlines()

point_list = []

for r in raw_info:
    x, y, vx, vy = re.match(PATTERN, r).groups()
    info = [[int(x), int(y)], [int(vx), int(vy)]]
    point_list.append(info)

#print point_list
cur_sec = 0
exact_sec = 0
min_range_x = min_range_y = MAX_RANGE
snapshot_pts = None


def snapshot(ptlist):
    global min_range_x, min_range_y, snapshot_pts, cur_sec, exact_sec
    range_x, range_y, min_x, min_y = get_range(ptlist)
    #transformation = min(min_x, min_y)

    if range_x > MAX_RANGE or range_y > MAX_RANGE:
        return
    # if min_range_x > range_x:
    #     min_range_x = range_x
    #     snapshot_pts = copy.deepcopy(ptlist)
    if min_range_y > range_y:
        min_range_y = range_y
        snapshot_pts = copy.deepcopy(ptlist)
        exact_sec = cur_sec


def print_pts(ptlist):
    global min_range_x, min_range_y, snapshot_pts
    range_x, range_y, min_x, min_y = get_range(ptlist)
    #transformation = min(min_x, min_y)

    if range_x > MAX_RANGE or range_y > MAX_RANGE:
        return
    print 'Range: ', range_x, range_y
    dotmap = ['.'] * range_x * range_y
    for pt in ptlist:
        trans_x = pt[P_IDX][X_IDX] - min_x
        trans_y = pt[P_IDX][Y_IDX] - min_y
        dotmap[trans_x + trans_y * range_x] = '#'

    for y in range(0, range_y):
        print ''.join(dotmap[y * range_x: (y + 1) * range_x])

    print '\n' * 2


def get_range(ptlist):
    min_x = min([pt[P_IDX][X_IDX] for pt in ptlist])
    max_x = max([pt[P_IDX][X_IDX] for pt in ptlist])
    min_y = min([pt[P_IDX][Y_IDX] for pt in ptlist])
    max_y = max([pt[P_IDX][Y_IDX] for pt in ptlist])
    range_x = max_x - min_x + 1
    range_y = max_y - min_y + 1
    return range_x, range_y, min_x, min_y


def move_pts(ptlist):
    for pt in ptlist:
        pt[P_IDX][X_IDX] += pt[V_IDX][X_IDX]
        pt[P_IDX][Y_IDX] += pt[V_IDX][Y_IDX]


print 'Origin:'
print_pts(point_list)


while cur_sec < MAX_SEC:
    cur_sec += 1
    #print 'Second: ', cur_sec
    move_pts(point_list)
    snapshot(point_list)

print 'Right time:', exact_sec
print_pts(snapshot_pts)

