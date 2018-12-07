#!/usr/bin/env python
import re

I_ID = 0
I_LEFT = I_ID + 1
I_TOP = I_LEFT + 1
I_WIDTH = I_TOP + 1
I_HEIGHT = I_WIDTH + 1

max_w = max_h = 0
max_w_id = max_h_id = 0

with open('q') as f:
    slist = f.readlines()

F_W = F_H = 1010
fabric = [0] * F_W * F_H
alist = []
idlist = []
oidset = set()
for s in slist:
    area = [int(x) for x in re.match(r'#(\d+) @ (\d+),(\d+): (\d+)x(\d+)', s).groups()]
    x = y = 0
    fid, fleft, ftop, fwidth, fheight = area
    #print area
    if fleft + fwidth > max_w:
        max_w = fleft + fwidth
        max_w_id = fid
    if ftop + fheight > max_h:
        max_h = ftop + fheight
        max_h_id = fid
    for y in range(fheight):
        for x in range(fwidth):
            pos = (ftop + y) * F_W + fleft + x
            if fabric[pos] == 0:
                fabric[pos] = fid
            else:
                fabric[pos] += 2000
                oidset.add(fid)
                oidset.add(fabric[pos] if fabric[pos] < 2000 else fabric[pos] - 2000)
    idlist.append(fid)
    alist.append(area)

#print len(alist)
#print 'No overlap: %d' %
print set(idlist) - oidset
print 'Width: %d@%d    <==>    Height: %d@%d' % (max_w, max_w_id, max_h, max_h_id)
print 'Count: %d' % len([x for x in fabric if x >= 2000])
