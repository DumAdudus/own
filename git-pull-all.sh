#!/usr/bin/env bash
# Credit: https://gist.github.com/grimzy/a1d3aae40412634df29cf86bb74a6f72

git fetch --all -v

git branch -r | grep -v '\->' | while read remote; do git branch --track "${remote#origin/}" "$remote"; done

git pull --all -v