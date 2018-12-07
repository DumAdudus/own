#!/usr/bin/env python
import string


def opposite(c1, c2):
    if c1 != c2:
        return c1.upper() == c2.upper()
    return False


def collapse(cstr, skip=None):
    index = -1
    chem = []
    for c in cstr:
        if skip and c in skip:
            continue
        if index == -1:
            chem.append(c)
            index += 1
            continue
        if opposite(c, chem[-1]):
            chem.pop()
            index -= 1
        else:
            chem.append(c)
            index += 1

    return chem


with open('q') as f:
    chemstr = f.read().strip('\n')


stripped = collapse(chemstr)
print 'a1: ', len(stripped)

r = {}
for c in string.ascii_lowercase:
    skip = c + c.upper()
    r[skip] = len(collapse(stripped, skip))
    #print skip, r[skip]

best = min(r, key=r.get)
print 'a2: ', best, r[best]
