#!/usr/bin/env python
import string
import copy

with open('q') as f:
    slist = f.readlines()
two = 0
three = 0
sublist = {}
for char in list(string.ascii_lowercase):
    sublist[char] = 0

for s in slist:
    countlist = copy.deepcopy(sublist)
    f=0
    for c in list(s.rstrip('\n')):
        countlist[c] += 1

    if 2 in countlist.values():
        two += 1
        f += 1
    if 3 in countlist.values():
        three += 1
        f += 1
    if f > 0:
        print '%s         %d' % (s.strip('\n'), f)

print 'two: %d       three: %d\nmul: %d' % (two, three, two*three)
