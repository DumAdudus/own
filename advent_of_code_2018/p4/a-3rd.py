#!/usr/bin/env python
from collections import defaultdict

lines = open('q').read().splitlines()
lines.sort()


def parseTime(line):
    words = line.split()
    date, time = words[0][1:], words[1][:-1]
    return int(time.split(':')[1])


C = defaultdict(int)
CM = defaultdict(int)
guard = None
asleep = None
for line in lines:
    if line:
        time = parseTime(line)
        if 'begins shift' in line:
            guard = int(line.split()[3][1:])
            asleep = None
        elif 'falls asleep' in line:
            asleep = time
        elif 'wakes up' in line:
            for t in range(asleep, time):
                CM[(guard, t)] += 1
                C[guard] += 1


def a1():
    best_guard = max(C, key=C.get)
    best_min = 0
    best_count = 0
    for k, v in CM.items():
        if best_guard in k:
            if v > best_count:
                best_count = v
                best_min = k[1]
    print 'a1:', best_guard, best_min, best_guard * best_min


def a2():
    best_guard = max(CM, key=CM.get)
    print best_guard, CM[best_guard], best_guard[0] * best_guard[1]

a1()
a2()
