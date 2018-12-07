#!/usr/bin/env python
import copy
import re
import string
from collections import defaultdict


with open('q') as f:
    raw_seq = f.read().splitlines()

PATTERN = r'Step (\w) .+ step (\w) .+'
pre_set = set()
post_set = set()
seq_dict = defaultdict(list)
dep_dict = defaultdict(list)

for l in raw_seq:
    pre, post = re.match(PATTERN, l).groups()
    seq_dict[pre].append(post)
    dep_dict[post].append(pre)
    pre_set.add(pre)
    post_set.add(post)

start_set = pre_set - post_set

print start_set
print post_set - pre_set
print seq_dict
print dep_dict

seq = []
count = len(pre_set) + 1
cur_set = copy.deepcopy(start_set)
while count > 0:
    print count, cur_set
    cur_p = min(cur_set)
    cur_set.discard(cur_p)
    seq.append(cur_p)

    next_set = set(seq_dict[cur_p])
    for s in next_set:
        if set(dep_dict[s]).issubset(set(seq)):
            cur_set.add(s)

    count -= 1

print ''.join(seq)


workers = defaultdict(int)
done = []
next_set = set()

BASESEC = 60
MAX_WORKER = 5

run_set = copy.deepcopy(start_set)
for s in run_set:
    workers[s] = BASESEC + string.ascii_uppercase.index(s) + 1

working = len(workers)
time_count = 0
next_set = set()
while working != 0:
    time_count += 1
    for step, t in workers.items():
        workers[step] -= 1
        if workers[step] == 0:
            print 'Done: ', step, 'at time: ', time_count
            working -= 1
            done.append(step)
            next_set.update(set(seq_dict[step]))
            next_set.difference_update(set(done))
            next_set.difference_update(set(workers.keys()))
            for s in next_set:
                if working == MAX_WORKER:
                    break
                if set(dep_dict[s]).issubset(set(done)):
                    print 'Add: ', s, 'at time: ', time_count
                    workers[s] = BASESEC + string.ascii_uppercase.index(s) + 1
                    working += 1
    for d in done:
        if d in workers:
            workers.pop(d)

print time_count
