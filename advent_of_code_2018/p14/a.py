#!/usr/bin/env python
from blist import blist

MATURE_POINT = 9
MATURE_POINT = 5
MATURE_POINT = 18
MATURE_POINT = 2018
MATURE_POINT = 554401
SCORE_COUNT = 10

scoreboard = blist([3, 7, 1, 0])
elf_pos = [0, 1]


def num2digits(num):
    return map(int, str(num))
    # return [int(x) for x in str(num)]


def list2str(l):
    return ''.join([str(x) for x in l])


def try_recipe():
    global scoreboard, elf_pos
    pos1 = elf_pos[0]
    pos2 = elf_pos[1]
    score1 = scoreboard[pos1]
    score2 = scoreboard[pos2]
    new_recipe = num2digits(score1 + score2)
    scoreboard.extend(new_recipe)
    newpos1 = (pos1 + score1 + 1) % len(scoreboard)
    newpos2 = (pos2 + score2 + 1) % len(scoreboard)
    elf_pos[0] = newpos1
    elf_pos[1] = newpos2


def main():
    # a1
    while len(scoreboard) < MATURE_POINT + SCORE_COUNT + 1:
        try_recipe()
    print ''.join([str(x) for x in scoreboard[MATURE_POINT: MATURE_POINT + SCORE_COUNT]])

    # a2
    start_bound = 0
    recipe_list = str(MATURE_POINT)
    while True:
        try_recipe()
        score_str = list2str(scoreboard[start_bound:])
        pos = score_str.find(recipe_list)
        if pos != -1:
            print 'Found in', score_str, 'at', start_bound + pos
            break
        else:
            start_bound = len(scoreboard) - len(recipe_list)

main()
