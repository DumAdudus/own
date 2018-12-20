#!/usr/bin/env python
import copy
import sys

with open(sys.argv[1]) as f:
    raw_info = f.read().splitlines()


INIT_HP = 200
POWER = 3
ID_BOUND = 100
MAX_DIST = 20
WALL = -2
CAVERN = -1

height = len(raw_info)
width = len(raw_info[0])

elves = dict()
goblins = dict()
caverns = dict()
walls = dict()

pic = [-2] * width * height
units = list()


def print_field():
    pic = ['#'] * width * height
    for c in caverns:
        x, y = c
        pic[y * height + x] = '.'
    for _, v in elves.items():
        x, y = v[0]
        pic[y * height + x] = 'E'
    for _, v in goblins.items():
        x, y = v[0]
        pic[y * height + x] = 'G'
    for i in range(0, height):
        print ''.join(pic[i * width: (i + 1) * width])


def init():
    global walls, caverns, elves, goblins, pic, units
    eid = 0
    gid = ID_BOUND
    y = 0
    for l in raw_info:
        x = 0
        for c in l:
            if c is '#':
                walls[(x, y)] = WALL
            elif c is '.':
                caverns[(x, y)] = CAVERN
            elif c is 'E':
                elves[eid] = [(x, y), INIT_HP, None]
                units.append(eid)
                eid += 1
            else:   # goblin
                goblins[gid] = [(x, y), INIT_HP, None]
                units.append(gid)
                gid += 1
            x += 1
        y += 1


def find_rival(uid):
    caves = copy.deepcopy(caverns)
    rival = None
    league = None
    rivals = None
    if uid < ID_BOUND:
        league = elves
        rivals = goblins
    else:
        league = goblins
        rivals = elves
    ux, uy = league[uid][0]
    rival_list = []
    work_queue = []
    queue_idx = 0
    hierarchy = {}
    dist = 1
    def add2q(cur_pos, d, prev_pos):
        if cur_pos in caves:
            if caves[cur_pos] == CAVERN:
                caves[cur_pos] = d
                work_queue.append((cur_pos, d))
                hierarchy[cur_pos] = prev_pos
        else:
            for k, v in rivals.items():
                if v[1] > 0 and cur_pos == v[0]:
                    hierarchy[cur_pos] = prev_pos
                    rival_list.append((k, d, cur_pos))

    add2q((ux, uy - 1), dist, (ux, uy))       # top
    add2q((ux - 1, uy), dist, (ux, uy))       # left
    add2q((ux + 1, uy), dist, (ux, uy))       # right
    add2q((ux, uy + 1), dist, (ux, uy))       # down
    while queue_idx < len(work_queue) and len(rival_list) == 0:
        # print work_queue
        nx, ny = work_queue[queue_idx][0]
        dist = work_queue[queue_idx][1] + 1
        add2q((nx, ny - 1), dist, (nx, ny))       # top
        add2q((nx - 1, ny), dist, (nx, ny))       # left
        add2q((nx + 1, ny), dist, (nx, ny))       # right
        add2q((nx, ny + 1), dist, (nx, ny))       # down
        queue_idx += 1

    rival = None
    jump_list = []
    if len(rival_list) > 0:
        rival = rival_list[0]
        cur_pos = rival[2]
        while True:
            jump_list.insert(0, cur_pos)
            if cur_pos == (ux, uy):
                break
            cur_pos = hierarchy[cur_pos]
    return rival, jump_list


def uid_cmp(l, r):
    if l < ID_BOUND:
        lx, ly = elves[l][0]
    else:
        lx, ly = goblins[l][0]
    if r < ID_BOUND:
        rx, ry = elves[r][0]
    else:
        rx, ry = goblins[r][0]
    if (lx, ly) == (rx, ry):
        return 0
    if ly < ry:
        return -1
    elif ly == ry:
        return lx - rx
    else:
        return 1


def move(u, next_pos, dist, targetid):
    if dist > 1:
        if u < ID_BOUND:
            league = elves
        else:
            league = goblins
        caverns[league[u][0]] = CAVERN
        caverns.pop(next_pos)
        league[u][0] = next_pos
        dist -= 1
        print u, 'move to', targetid

    if dist == 1:
        attack(u, targetid)


def attack(u1, u2):
    print u1, 'attack', u2
    if u2 < ID_BOUND:
        league = goblins
        rival = elves
    else:
        league = elves
        rival = goblins
    health = rival[u2][1] - POWER
    rival[u2][1] = health
    league[u1][2] = u2
    if health <= 0:
        caverns[rival[u2][0]] = CAVERN
        print u2, 'killed'
        for k, v in league.items():
            if v[2] == u2:
                league[k][2] = None


def get_rival(u):
    if u < ID_BOUND:
        league = elves
    else:
        league = goblins
    return league[u][2]


def inbattle(u):
    return bool(get_rival(u))


def alive(u):
    if u < ID_BOUND:
        league = elves
    else:
        league = goblins
    return league[u][1] > 0


init()
print_field()
rounds = 0
while len(elves) > 0 and len(goblins) > 0:
    rounds += 1
    for u in units:
        if not alive(u):
            continue
        if inbattle(u):
            attack(u, get_rival(u))
            continue
        rival, chain = find_rival(u)
        if rival:
            move(u, chain[1], rival[1], rival[0])
        else:
            print u, 'hold'

    units = [x for x in units if alive(x)]
    units.sort(cmp=uid_cmp)
    for k, v in elves.items():
        if v[1] <= 0:
            del elves[k]
    for k, v in goblins.items():
        if v[1] <= 0:
            del goblins[k]

    print_field()

health_sum = 0
survivor = None
if len(elves) > 0:
    survivor = elves
if len(goblins) > 0:
    survivor = goblins
health_sum = sum([v[1] for v in survivor.values()])
print survivor
print rounds, health_sum, rounds * health_sum

