#!/usr/bin/env python
import copy

with open('q') as f:
    raw_input = f.read().splitlines()

D_LEFT = '<'
D_RIGHT = '>'
D_UP = '^'
D_DOWN = 'v'

CROSS_TURN = list('rsl')    # reverse left, straight, right

t_height = len(raw_input)
t_width = max([len(r) for r in raw_input])

tracks = []
carts = {}
carts_pos = [0] * t_height * t_width

y = 0
cart_id = 0
for r in raw_input:
    x = 0
    track = list(r)
    pos = [0] * len(track)
    for c in r:
        if c in D_LEFT + D_RIGHT + D_UP + D_DOWN:
            cart = [c, x, y, copy.deepcopy(CROSS_TURN)]
            cart_id += 1
            carts[cart_id] = cart
            carts_pos[y * t_width + x] = cart_id
            if c in D_LEFT + D_RIGHT:
                track[x] = '-'
            else:
                track[x] = '|'

        x += 1
    tracks.append(track)
    y += 1

for t in tracks:
    print ''.join(t)


carts_on_track = len(carts)
exclude_list = [0]

tick = 0
collide = False
crash_done = False
while not collide:
    cart_idx = 0
    new_pos = copy.deepcopy(carts_pos)
    if carts_on_track == 1:
        crash_done = True
    for p in carts_pos:
        if p in exclude_list:
            continue
        cart = carts[p]
        d = cart[0]
        nd = d
        x, y = cart[1:3]
        nx = x
        ny = y
        cross = cart[3]
        guide = tracks[y][x]
        if guide is '+':
            turn_to = cross.pop()
            if turn_to is 'l':
                if d in '<>':
                    guide = '/'
                else:
                    guide = '\\'
            elif turn_to is 's':
                if d in '<>':
                    guide = '-'
                else:
                    guide = '|'
            else:
                if d in '<>':
                    guide = '\\'
                else:
                    guide = '/'
            #print 'Node', p, 'meet + and move', turn_to, guide
            if len(cross) == 0:
                cross = copy.deepcopy(CROSS_TURN)

        if guide + d in ['-<', '/v', '\\^']:
            nx = x - 1
            nd = D_LEFT
        elif guide + d in ['->', '/^', '\\v']:
            nx = x + 1
            nd = D_RIGHT
        elif guide + d in ['|^', '/>', '\\<']:
            ny = y - 1
            nd = D_UP
        elif guide + d in ['|v', '/<', '\\>']:
            ny = y + 1
            nd = D_DOWN
        else:
            assert('Something wrong')

        dest_pos = ny * t_width + nx
        if new_pos[dest_pos] != 0:
            print 'Collide: ({}, {}) {} ==> {}'.format(nx, ny, p, new_pos[dest_pos])
            carts_on_track -= 2
            exclude_list.append(p)
            exclude_list.append(new_pos[dest_pos])
            new_pos[y * t_width + x] = 0
            new_pos[dest_pos] = 0
            print [x for x in new_pos if x != 0]
        else:
            #print 'Node %d move %s (%d, %d) => (%d, %d)' % (p, nd, x, y, nx, ny)
            new_pos[y * t_width + x] = 0
            new_pos[dest_pos] = p
            carts[p] = [nd, nx, ny, cross]
            if crash_done:
                print 'Final cart %s move (%d, %d) => (%d, %d)' % (p, x, y, nx, ny)
                collide = True
                break
    carts_pos = new_pos
    tick += 1

