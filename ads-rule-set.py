#!/usr/bin/env python

import json

singbox_template = '{"version": 2, "rules": [{"domain": [], "domain_suffix": [], "domain_regex": []}]}'

ruleset = json.loads(singbox_template)

FULL_MATCH_PREFIX = "full:"
REGEX_MATCH_PREFIX = 'regexp:'

with open("all.ads.conf", "r") as f:
  lines = f.read().splitlines()

rules = ruleset["rules"][0]

for line in lines:
  if line.startswith(FULL_MATCH_PREFIX):
    rules["domain"].append(line.removeprefix(FULL_MATCH_PREFIX))
  elif line.startswith(REGEX_MATCH_PREFIX):
    rules["domain_regex"].append(line.removeprefix(REGEX_MATCH_PREFIX))
  else:
    rules["domain_suffix"].append(line)

with open('ads-ruleset.json', 'w') as f:
  json.dump(ruleset, f)