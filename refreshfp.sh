#!/bin/bash

scriptfolder=$(dirname $(realpath $0))
. ${scriptfolder}/shlib.sh

if [ ! $# -eq 1 ]; then
    read -p "Appliance: " appliance
else
    appliance=$1
fi

ssh_refreshHostKey ${appliance}
