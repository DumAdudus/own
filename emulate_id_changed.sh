#!/bin/bash

scriptfolder=$(dirname $(readlink -f $0))
. ${scriptfolder}/shlib.sh

target=

if [ ! $# -eq 1 ]; then
    read -p "Provide a target: " target
else
    target=$1
fi

target=$(ssh_getHostname ${target})
hashKey=$(ssh-keygen -F $target)

if [ -z "$hashKey" ]; then
    echo 'No key found!'
    exit 1
fi

hashKey=$(sed_escape_backslash ${hashKey##* })
fakeKey=$(sed_escape_backslash 'AAAAB3NzaC1yc2EAAAABIwAAAQEAwRKwyn/VOaw5IBbodCx90EklZuZ7/4/pnMXqt/hC2rROAhNdhs5WIYNpFFg2wNWbQD7wUfXlLBtWSz65LDsw0YhNJv54geBlsmwjpk57NaWR3F62UshAWXicWHF/xdXxrLqJJaCEfemzB592wV1VFOj7dH4eL1OT2kcMmHzlptbzh2jS3l386DDcQL4x9E1ExsGAnqXDX55Rld5jGLd0SNbDqsqZKgrVP6jsB4ZVM5yYoDzAigE74/ZfyUlEbhnKnj6ZbvthJiLWJ4PZOnhd5uckSXjb0ePkM8+vOUYcWDLd+hzFWJlBZAIXt37dNboDijGMnOIYbhTyD4A+XlqIcw==')
sed -i "s/${hashKey}/${fakeKey}/g" ~/.ssh/known_hosts
