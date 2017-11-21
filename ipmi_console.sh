#!/bin/bash
set -u

scriptfolder=$(dirname $(readlink -f $0))
. ${scriptfolder}/shlib.sh
. ${scriptfolder}/applib.sh

if [ ! $# -eq 1 ]; then
    read -p "Appliance: " appliance
else
    appliance=$1
fi

hostname=$(expandname ${appliance})
fqdn=$(ssh_getHostname $hostname)
ipmihost=${fqdn/$hostname/$hostname-nm}

echo Connecting to $appliance ...
ipmi_params="-I lanplus -H $ipmihost -U sysadmin -P P@ssw0rd"
${SSH} lab-springboard -t ipmitool ${ipmi_params} sol deactivate
${SSH} lab-springboard -t ipmitool -e % ${ipmi_params} sol activate
