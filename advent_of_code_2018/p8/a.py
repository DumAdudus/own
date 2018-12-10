#!/usr/bin/env python
import string

with open('q') as f:
    raw_seq = f.read().strip('\n').split(' ')

SC_IDX = 0
S_IDX = 1
MC_IDX = 2
M_IDX = 3
SEAT_IDX = 4
B_IDX = 5
V_IDX = 6

node_info = {}
node_stack = []
node_idx = 0
seq_idx = 0
parent_map = {}

ascii_idx = 1

pop_parent = False


def lastson(son):
    if son not in parent_map:
        return False
    p_node = node_info[parent_map[son]]
    return p_node[SEAT_IDX] == p_node[SC_IDX] + 1


while seq_idx < len(raw_seq):
    if pop_parent:
        pop_parent = False
        node = node_stack.pop()
        node_i = node_info[node]
        node_i[M_IDX] = [int(x) for x in raw_seq[seq_idx: seq_idx + node_i[MC_IDX]]]
        for m in node_i[M_IDX]:
            if m > node_i[SC_IDX] or m == 0:
                continue
            node_i[V_IDX] += node_info.get(node_i[S_IDX][m - 1])[V_IDX]
        #print '::', node, '>', node_i[V_IDX], node_i[S_IDX], node_i[M_IDX]
        if len(node_stack) == 0:
            break
        seq_idx += node_i[MC_IDX]
        node_info[node_stack[-1]][SEAT_IDX] += 1
        if lastson(node):
            pop_parent = True
            #print node, '==>', parent_map[node]
    else:
        #print node_stack
        if len(node_stack) == 0:
            node_idx = 0
        else:
            parent = node_stack[-1]
            node_idx = node_info[parent][B_IDX] + node_info[parent][SEAT_IDX]
            #print 'process: ', node_idx, parent
        cur_node = node_idx

        son_count = int(raw_seq[seq_idx])
        sons = None
        meta_count = int(raw_seq[seq_idx + 1])
        metas = []
        cur_seat = 1
        seq_idx += 2
        value = 0

        #print cur_node, son_count, sons, meta_count
        if son_count == 0:
            metas = [int(x) for x in raw_seq[seq_idx: seq_idx + meta_count]]
            seq_idx += meta_count
            node_info[node_stack[-1]][SEAT_IDX] += 1
            value = sum(metas)
            #print '::', cur_node, '>', value
            if lastson(cur_node):
                pop_parent = True
                #print cur_node, '-->', parent_map[cur_node]
        else:
            node_stack.append(cur_node)
            sons = range(ascii_idx, ascii_idx + son_count)
            for s in sons:
                parent_map[s] = cur_node
        idx_base = ascii_idx - 1
        node_info[cur_node] = [son_count, sons, meta_count, metas, cur_seat, idx_base, value]
        ascii_idx += son_count
        #print cur_node, node_info[cur_node]

meta_sum = sum([sum(v[M_IDX]) for _, v in node_info.items()])
#print node_stack
print meta_sum
print node_info[0]
