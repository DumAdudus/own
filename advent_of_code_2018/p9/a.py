#!/usr/bin/env python
from collections import defaultdict

PLAYERS = 9
MAX_MARBLE = 25

PLAYERS = 10
MAX_MARBLE = 1618

PLAYERS = 13
MAX_MARBLE = 7999

PLAYERS = 17
MAX_MARBLE = 1104

PLAYERS = 21
MAX_MARBLE = 6111

PLAYERS = 30
MAX_MARBLE = 5807

PLAYERS = 432
MAX_MARBLE = 7101900

DIV = 23
JUMP = 2
BACKJUMP = 7

seq = [0]
seq_idx = 0

p_idx = 0
scores = defaultdict(int)


def cycle_player():
    global p_idx
    if p_idx == PLAYERS:
        p_idx = 1
    else:
        p_idx += 1


def jump():
    global seq_idx, seq
    next_idx = seq_idx + JUMP
    if next_idx > len(seq):
        seq_idx = next_idx - len(seq)
    else:
        seq_idx = next_idx


def counter_jump():
    global seq_idx, seq
    next_idx = seq_idx - BACKJUMP
    if next_idx < 0:
        seq_idx = len(seq) - abs(next_idx)
    else:
        seq_idx = next_idx


for m in range(1, MAX_MARBLE):
    cycle_player()
    #print p_idx, seq
    if m >= DIV and m % DIV == 0:
        counter_jump()
        scores[p_idx] += m + seq[seq_idx]
        #print m, seq[seq_idx]
        seq.pop(seq_idx)
        continue

    jump()
    seq.insert(seq_idx, m)

max_player = max(scores, key=scores.get)
print max_player, scores[max_player]
