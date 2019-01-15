#!/usr/bin/env python
from collections import defaultdict

with open('q') as f:
    raw_regex = f.read()

exclude = ('^', '$')
raw_paths = [c for c in raw_regex if c not in exclude]
branch_id = parent_id = 0
id_seq = 0
idx = 0
parent_map = {0: 0}
new_branch = False
branches = defaultdict(list)
branch_info = defaultdict(list)
sub_group = defaultdict(list)
branch_info[0] = [0, -1]
while idx < len(raw_paths):
    if raw_paths[idx] == '(':
        parent_id = branch_id
        id_seq += 1
        branch_id = id_seq
        parent_map[branch_id] = parent_id
        branches[parent_id].append(branch_id)
        branch_info[branch_id] = [idx + 1, -1]
    elif raw_paths[idx] == '|':
        branch_info[branch_id][1] = idx
        id_seq += 1
        branch_id = id_seq
        parent_map[branch_id] = parent_id
        branches[parent_id].append(branch_id)
        branch_info[branch_id] = [idx + 1, -1]
    elif raw_paths[idx] == ')':
        branch_info[branch_id][1] = idx
        sub_group[parent_id].append(branch_id)
        branch_id = parent_map[branch_id]
        parent_id = parent_map[parent_id]

    idx += 1

print branches
print branch_info
print sub_group
print id_seq

# @profile
def mix_2lists(l1, l2):
    # return [x + y for x, y in zip(l1, l2)]
    final = list()
    for l in l1:
        for k in l2:
            final.append(l + k)
    return final

# @profile
def get_seg(s, e):
    return ''.join(c for c in raw_paths[s : e] if c not in '(|)')


# def get_branch_strs(bid):
#     s, e = branch_info[bid]
#     if bid not in branches:
#         return [''.join(raw_paths[s:e])]

#     first_b = branches[bid][0]
#     front = get_seg(s, branch_info[first_b][0])
#     strs = [front]
#     i = 0
#     sub_branch = branches[bid]
#     grp_strs = []
#     while i < len(sub_branch):
#         b = sub_branch[i]
#         postfixes = get_branch_strs(b)
#         grp_strs.extend(postfixes)
#         if b in sub_group[bid]:
#             strs = mix_2lists(strs, grp_strs)
#             grp_strs = []
#             if i < len(sub_branch) - 1:
#                 nb = sub_branch[i + 1]
#                 segment = get_seg(branch_info[b][1], branch_info[nb][0])
#                 strs = mix_2lists(strs, [segment])
#         i += 1

#     last_b = branches[bid][-1]
#     rear = get_seg(branch_info[last_b][1], e)
#     strs = mix_2lists(strs, [rear])
#     return strs

# paths = get_branch_strs(0)
# print max([len(x) for x in paths])

# get all leaves
pending_list = range(0, id_seq + 1)
id_path = dict()
for i in pending_list:
    if i not in branches:
        s, e = branch_info[i]
        id_path[i] = [e - s]

print id_path

# @profile
def pop_pending():
    for i in id_path:
        try:
            pending_list.remove(i)
        except ValueError:
            pass

    print 'Left: %d' % len(pending_list)

pop_pending()

# @profile
def main():
    while True:
        for bid in pending_list:
            sub_branch = branches[bid]
            # if set(sub_branch) <= set(id_path.keys()):
            if all(x in id_path for x in sub_branch):
                s, e = branch_info[bid]
                first_b = branches[bid][0]
                front = len(get_seg(s, branch_info[first_b][0]))
                strs = [front]
                i = 0
                grp_strs = []
                while i < len(sub_branch):
                    b = sub_branch[i]
                    postfixes = id_path[b]
                    grp_strs.extend(postfixes)
                    if b in sub_group[bid]:
                        strs = mix_2lists(strs, [max(grp_strs)])
                        grp_strs = []
                        if i < len(sub_branch) - 1:
                            nb = sub_branch[i + 1]
                            segment = len(get_seg(branch_info[b][1], branch_info[nb][0]))
                            strs = mix_2lists(strs, [segment])
                    i += 1

                last_b = branches[bid][-1]
                rear = len(get_seg(branch_info[last_b][1], e))
                strs = mix_2lists(strs, [rear])
                id_path[bid] = strs
                for s in sub_branch:
                    del id_path[s]

        pop_pending()
        if len(pending_list) == 0:
            break

    print id_path
    # print max(id_path[0])

main()
