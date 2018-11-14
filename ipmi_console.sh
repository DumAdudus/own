#!/bin/bash
set -u

scriptfolder=$(dirname $(realpath $0))
. ${scriptfolder}/shlib.sh
. ${scriptfolder}/applib.sh

if [ ! $# -eq 1 ]; then
    read -p "Appliance: " appliance
else
    appliance=$1
fi

hostname=$(get_short_name "$appliance")
ipmihost=$(getipmihost "$hostname")

echo "Connecting to $appliance ..."
ipmi_params="-I lanplus -H $ipmihost -U sysadmin -P P@ssw0rd"
${SSH} lab-springboard -- ipmitool "$ipmi_params" sol deactivate
${SSH} lab-springboard -- ipmitool -e % "$ipmi_params" sol activate
