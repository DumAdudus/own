#!/usr/bin/env python

import re
from collections import defaultdict


dists_calc = 0


class Nanobot:
    def __init__(self, x, y, z, r):
        self.x = x
        self.y = y
        self.z = z
        self.r = r

    def __str__(self):
        return '{:11d}  {:11d}  {:11d}  {:11d}\n'.format(self.x, self.y, self.z, self.r)

    def __repr__(self):
        return self.__str__()

    def dist(self, bot):
        global dists_calc
        dists_calc += 1
        d = abs(bot.x - self.x) + abs(bot.y - self.y) + abs(bot.z - self.z)
        return d

    def in_my_range(self, bot):
        if self.dist(bot) > self.r:
            return False
        return True

    @classmethod
    def fromraw(cls, raw):
        p = re.compile('.+<([0-9-]+),([0-9-]+),([0-9-]+)>.+r=([0-9-]+)')
        m = p.match(raw)
        x, y, z, r = map(int, m.groups())
        return cls(x, y, z, r)


bots = dict()

bot_id = 0
with open('e2') as f:
    for line in f.read().splitlines():
        bot = Nanobot.fromraw(line)
        bots[bot_id] = bot
        bot_id += 1


def p1():
    max_id = max(bots, key=lambda x: bots[x].r)
    dists = defaultdict(set)

    for bid, bot in bots.items():
        if bid != max_id:
            continue
        for nbid, nbot in bots.items():
            if nbid == bid:
                dists[bid].add(bid)
                continue
            if bot.in_my_range(nbot):
                dists[bid].add(nbid)

    # max_id = max(dists, key=lambda x: len(dists[x]))
    print max_id, len(dists[max_id])
    print dists_calc


def calc_overlap(id1, id2):
    b1 = bots[id1]
    b2 = bots[id2]



def p2():
    calc_overlap(0, 193)

# for b in bots.values():
#     print '{:11d}  {:11d}  {:11d}  {:11d}'.format(b.x, b.y, b.z, b.r)
# p1()
# p2()
