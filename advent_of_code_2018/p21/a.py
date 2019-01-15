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
    if act == assign:
        ra.set(str(op.C), act(op.A, 0))
    else:
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
        '3': 'reg3',
        '4': 'reg4',
        '5': 'reg5'
    }

    def __init__(self, r0 = 0, r1 = 0, r2 = 0, r3 = 0, r4 = 0, r5 = 0):
        self.reg0 = r0
        self.reg1 = r1
        self.reg2 = r2
        self.reg3 = r3
        self.reg4 = r4
        self.reg5 = r5

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
        return str([self.reg0, self.reg1, self.reg2, self.reg3, self.reg4, self.reg5])

    def get(self, name):
        return self.__getattr__(name)

    def set(self, name, value):
        return self.__setattr__(name, value)


class Op(object):
    def __init__(self, code, A, B, C):
        self.opcode = code
        self.A = A
        self.B = B
        self.C = C

    def __str__(self):
        return str([self.opcode.__name__, self.A, self.B, self.C])

    def __repr__(self):
        return str(self)

    def run(self, reg):
        return self.opcode(self, reg)

    @classmethod
    def from_raw(cls, raw):
        seq = raw.split()
        return cls(globals()[seq[0]], int(seq[1]), int(seq[2]), int(seq[3]))

f = open('q')
ip_reg = f.readline().split()[1]

oplist = list()
for line in f.read().splitlines():
    op = Op.from_raw(line)
    oplist.append(op)


ip = 0
reg = Reg()

# ip = 18
# reg = Reg(0, 14535837, 256, 0, 18, 65536)

ip = 19
reg = Reg(0, 14535837, 254, 255, 19, 65536)
reg.reg0 = 5970144

# reg = Reg(0, 3712647,91, 92, 19, 23320)


while True:
    cur_op = oplist[ip]
    reg.set(ip_reg, ip)
    nreg = cur_op.run(reg)
    print "ip:", ip, reg, cur_op, nreg
    ip = nreg.get(ip_reg)
    ip += 1
    if ip >= len(oplist):
        break
    reg = nreg

print reg



