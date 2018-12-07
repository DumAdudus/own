#!/usr/bin/env python
with open('q') as f:
    numlist = f.readlines()
f = 0
i = 0
sumlist = []
while f == 0:
    for num in numlist:
        i += int(num)
        if i in sumlist:
            print 'Found %d' % i
            f = 1
            break
        sumlist.append(i)
