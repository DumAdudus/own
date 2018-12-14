#!/usr/bin/env python
import re


GENERATIONS = 300
PADDINGV = 300
LOOKAHEAD = '(?={})'
#LOOKAHEAD = '{}'

with open('q') as f:
    raw_info = f.read().splitlines()

init_state = '.' * 10 + raw_info[0].split(': ')[1] + '.' * PADDINGV

cur_state = list(init_state)
zero_pos = init_state.index('#')
print zero_pos

grow_pattern_list = []
for l in raw_info[2:]:
    p = l[0:5]
    r = l[9]
    grow_pattern_list.append((p, r))

print '          0:', ''.join(cur_state)
gen = 0
while gen < GENERATIONS:
    gen += 1
    stage_state = ['.'] * len(init_state)
    for p in grow_pattern_list:
        for m in re.finditer(LOOKAHEAD.format(p[0].replace('.', '\\.')), ''.join(cur_state)):
            stage_state[m.start() + 2] = p[1]
    cur_state = stage_state
    #print ''.join(cur_state)
    nsum = 0
    for m in re.finditer('#', ''.join(cur_state)):
        nsum += m.start() - zero_pos
    print '{:4d} {:6d}:'.format(gen, nsum), ''.join(cur_state)

nsum = 0
for m in re.finditer('#', ''.join(cur_state)):
    nsum += m.start() - zero_pos

print nsum
