#!/usr/bin/env python
import difflib

with open('q') as f:
    slist = f.readlines()

size = len(slist)
f = False

i1 = i2 = 0
while i1 < size and not f:
    i2 = i1 + 1
    a = slist[i1]
    while i2 < size:
        b = slist[i2]
        matches = difflib.SequenceMatcher(None, a, b).get_matching_blocks()
        if len(matches) == 3 and matches[0].a == 0 and matches[0].a + matches[0].size + 1 == matches[1].a:
            print '%s%s' % (a[:matches[0].size], a[matches[1].a:matches[1].a + matches[1].size])
            f = True
            break
        i2 += 1
    i1 += 1
