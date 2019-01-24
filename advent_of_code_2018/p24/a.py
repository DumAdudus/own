#!/usr/bin/env python
import enum
import re
import copy


@enum.unique
class AttackType(enum.Enum):
    DEF = 0
    RADIATION = 1
    FIRE = 2
    SLASHING = 3
    BLUDGEONING = 4
    COLD = 5


class Clan(enum.Enum):
    IMMUNE = 0
    INFECTION = 1


class Group(object):
    def __init__(self):
        self.clan = None
        self.id = 0
        self.units = 0
        self.health = 0
        self.weaknesses = []
        self.immunities = []
        self.damage = 0
        self.attack_type = AttackType.DEF
        self.initiative = 0

    def __repr__(self):
        s = ''
        for k, v in self.__dict__.items():
            s += k + ': ' + str(v) + '\n'
        return s + '\n'

    @classmethod
    def fromraw(cls, raw):
        # 2202 units each with 4950 hit points (weak to fire; immune to slashing) with an attack that does 18 cold damage at initiative 2
        p = re.compile('(\d+) units each with (\d+) hit points (\(.+\) )?with an attack that does (\d+) (\w*) damage at initiative (\d+)')
        m = p.match(raw)
        g = Group()
        g.units = int(m.group(1))
        g.health = int(m.group(2))
        if m.group(3):
            for s in map(str.strip, m.group(3)[1:-2].split(';')):
                for t in re.split(', ', re.sub('\w+ to ', '', s)):
                    if s.startswith('imm'):
                        g.immunities.append(AttackType[t.upper()])
                    else:
                        g.weaknesses.append(AttackType[t.upper()])
        g.damage = int(m.group(4))
        g.attack_type = AttackType[m.group(5).upper()]
        g.initiative = int(m.group(6))
        return g


imm_origin = []
inf_origin = []
battle_queue = []


def init(file):
    global imm_origin, inf_origin
    imm_id = 1
    inf_id = 1
    with open(file) as f:
        imm_league = False
        for line in f.read().splitlines():
            if len(line) == 0:
                continue
            if line == 'Immune System:':
                imm_league = True
                continue
            if line == 'Infection:':
                imm_league = False
                continue
            g = Group.fromraw(line)
            if imm_league:
                g.clan = Clan.IMMUNE
                g.id = imm_id
                imm_id += 1
                imm_origin.append(g)
            else:
                g.clan = Clan.INFECTION
                g.id = inf_id
                inf_id += 1
                inf_origin.append(g)


def calc_dmg(g1, g2):
    dmg = 0
    if g1.attack_type not in g2.immunities:
        dmg = calc_ep(g1)
        if g1.attack_type in g2.weaknesses:
            dmg *= 2
    return dmg


def calc_ep(g):
    # calc effective power
    gdmg = g.damage
    if g.clan == Clan.IMMUNE:
        gdmg += immune_boost
    return g.units * gdmg


def select_rival(group, imm_queue, inf_queue):
    enimies = imm_queue
    if group.clan == Clan.IMMUNE:
        enimies = inf_queue

    max_dmg = 0
    rival = None
    for e in enimies:
        dmg = calc_dmg(group, e)
        if dmg == 0:
            continue
        # compare damage
        if dmg > max_dmg:
            max_dmg = dmg
            rival = e
        elif dmg == max_dmg:
            # compare effective power
            rep = calc_ep(rival)
            eep = calc_ep(e)
            if eep > rep:
                rival = e
            elif eep == rep:
                # compare initiative
                if e.initiative > rival.initiative:
                    rival = e
    return rival


def select_cmp(l, r):
    lep = calc_ep(l)
    rep = calc_ep(r)
    if lep > rep:
        return 1
    elif lep < rep:
        return -1
    else:
        if l.initiative > r.initiative:
            return 1
        elif l.initiative < r.initiative:
            return -1
        else:
            return 0


def target_select():
    global battle_queue
    select_queue = []
    select_queue.extend(imm_sys)
    select_queue.extend(inf_sys)
    select_queue.sort(cmp=select_cmp, reverse=True)
    # print mixed_queue
    imm_q = copy.copy(imm_sys)
    inf_q = copy.copy(inf_sys)
    for g in select_queue:
        # print '{}{}\t\t{}\t\t{}\t\t{}'.format(g.clan, g.id, g.units, g.damage, calc_ep(g))
        rival = select_rival(g, imm_q, inf_q)
        if rival:
            battle_queue.append((g, rival))
            if rival.clan == Clan.IMMUNE:
                imm_q.remove(rival)
            else:
                inf_q.remove(rival)


def attack():
    global battle_queue, imm_sys, inf_sys
    battle_queue.sort(key=lambda x: x[0].initiative, reverse=True)
    for attacker, defender in battle_queue:
        if attacker.units <= 0:
            continue
        dmg = calc_dmg(attacker, defender)
        kill = dmg / defender.health
        defender.units -= kill
        print '{}{} => {}{}, dmg: {}, kill: {}'.format(attacker.clan, attacker.id, defender.clan, defender.id, dmg, kill)
    # print battle_queue
    battle_queue = []
    imm_sys = [x for x in imm_sys if x.units > 0]
    inf_sys = [x for x in inf_sys if x.units > 0]


def print_survivor():
    survivors = imm_sys
    if len(inf_sys) > 0:
        survivors = inf_sys
    print survivors
    print sum(x.units for x in survivors)



init('q')
last_boost = immune_boost = 42
imm_sys = []
inf_sys = []

while True:
    imm_sys = copy.deepcopy(imm_origin)
    inf_sys = copy.deepcopy(inf_origin)
    print 'boost:', immune_boost

    while len(imm_sys) > 0 and len(inf_sys) > 0:
        target_select()
        attack()
    if len(imm_sys) > 0:
        print 'immune win', immune_boost
        break
    else:
        last_boost = immune_boost
        immune_boost += 1

print_survivor()
