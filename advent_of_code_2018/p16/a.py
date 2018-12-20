#!/usr/bin/env python
import copy
import re
from collections import defaultdict

calcs = list()
final_map = dict()

def add(l, r):
    return l + r

def mul(l, r):
    return l * r

def ban(l, r):
    return l & r

def bor(l, r):
    return l | r

def assign(l, r):
    return l

def grt(l, r):
    if l > r:
        return 1
    else:
        return 0

def eq(l, r):
    if l == r:
        return 1
    else:
        return 0

def rr(op, reg, act):
    ra = copy.copy(reg)
    ra.set(str(op.C), act(reg.get(str(op.A)), reg.get(str(op.B))))
    return ra

def ri(op, reg, act):
    ra = copy.copy(reg)
    ra.set(str(op.C), act(reg.get(str(op.A)), op.B))
    return ra

def ir(op, reg, act):
    ra = copy.copy(reg)
    ra.set(str(op.C), act(op.A, reg.get(str(op.B))))
    return ra

def addr(op, reg):
    return rr(op, reg, add)

def addi(op, reg):
    return ri(op, reg, add)

def mulr(op, reg):
    return rr(op, reg, mul)

def muli(op, reg):
    return ri(op, reg, mul)

def banr(op, reg):
    return rr(op, reg, ban)

def bani(op, reg):
    return ri(op, reg, ban)

def borr(op, reg):
    return rr(op, reg, bor)

def bori(op, reg):
    return ri(op, reg, bor)

def setr(op, reg):
    return rr(op, reg, assign)

def seti(op, reg):
    return ir(op, reg, assign)

def gtir(op, reg):
    return ir(op, reg, grt)

def gtri(op, reg):
    return ri(op, reg, grt)

def gtrr(op, reg):
    return rr(op, reg, grt)

def eqir(op, reg):
    return ir(op, reg, eq)

def eqri(op, reg):
    return ri(op, reg, eq)

def eqrr(op, reg):
    return rr(op, reg, eq)


opcodes = [addr, addi, mulr, muli, banr, bani, borr, bori, setr, seti, gtir, gtri, gtrr, eqir, eqri, eqrr]

class Reg(object):
    REG_PATTERN = r'\[|\]|, '
    aliases = {
        '0': 'reg0',
        '1': 'reg1',
        '2': 'reg2',
        '3': 'reg3'
    }

    def __init__(self, r0 = 0, r1 = 0, r2 = 0, r3 = 0):
        self.reg0 = r0
        self.reg1 = r1
        self.reg2 = r2
        self.reg3 = r3

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __setattr__(self, name, value):
        attr = self.aliases.get(name, name)
        object.__setattr__(self, attr, value)

    def __getattr__(self, name):
        if name == "aliases":
            raise AttributeError  # http://nedbatchelder.com/blog/201010/surprising_getattr_recursion.html
        attr = self.aliases.get(name, name)
        #return getattr(self, name) #Causes infinite recursion on non-existent attribute
        return object.__getattribute__(self, attr)

    def __str__(self):
        return str([self.reg0, self.reg1, self.reg2, self.reg3])

    def get(self, name):
        return self.__getattr__(name)

    def set(self, name, value):
        return self.__setattr__(name, value)

    @classmethod
    def from_raw(cls, raw):
        seq = re.split(Reg.REG_PATTERN, raw)
        return cls(int(seq[1]), int(seq[2]), int(seq[3]), int(seq[4]))


class Op(object):
    def __init__(self, code, A, B, C):
        self.opcode = code
        self.A = A
        self.B = B
        self.C = C

    def __str__(self):
        if self.opcode in final_map:
            return str([final_map.get(self.opcode).__name__, self.A, self.B, self.C])
        else:
            return str([self.opcode, self.A, self.B, self.C])

    @classmethod
    def from_raw(cls, raw):
        seq = raw.split()
        return cls(int(seq[0]), int(seq[1]), int(seq[2]), int(seq[3]))

calc_map = defaultdict(int)

count = 0
f = open('q')
while True:
    line1 = f.readline()
    if 'Before' not in line1:
        break

    line2 = f.readline()
    line3 = f.readline()
    _ = f.readline()

    r_before = Reg.from_raw(line1)
    r_after = Reg.from_raw(line3)
    op = Op.from_raw(line2)
    matched = 0
    code_list = list()
    for code in opcodes:
        if code(op, r_before) == r_after:
            calc_map[(op.opcode, code)] += 1
            matched += 1
    if matched >= 3:
        count += 1

print count

p2_init = r_after

codes_map = defaultdict(list)

for c in range(0, 16):
    for k in calc_map:
        if c in k:
            codes_map[c].append(k[1])

print codes_map

while True:
    code = None
    occupied = None
    for k, v in codes_map.items():
        if len(v) == 1:
            code = k
            occupied = v[0]
            final_map[k] = occupied
            print 'found', k, occupied.__name__
            break
    if not occupied:
        break
    del codes_map[code]
    for k, v in codes_map.items():
        if len(v) > 1 and occupied in v:
            codes_map[k].remove(occupied)

cur_reg = copy.copy(p2_init)
cur_reg = Reg(0, 0, 0, 0)
while True:
    line = f.readline()
    if not line:
        break
    if len(line) == 1:
        print line
        continue
    op = Op.from_raw(line.rstrip('\n'))
    cur_reg = final_map[op.opcode](op, cur_reg)
    print 'op', op
    print 'reg', cur_reg

print cur_reg
