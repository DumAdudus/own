#!/bin/bash

scriptfolder=$(dirname "$(readlink -f "$0")")
. "${scriptfolder}/shlib.sh"

if [ ! $# -eq 1 ]; then
    read -p "Appliance: " appliance
else
    appliance=$1
fi

hostname=$(ssh_getHostname ${appliance})
ssh_refreshHostKey ${hostname}

tmpf=$(mktemp -p "$scriptfolder")
trap 'rm -rf $tmpf' EXIT

pass='P@ssw0rd'

echo "echo $pass" > "$tmpf" && chmod u+x "$tmpf"
DISPLAY=bogus SSH_ASKPASS=$tmpf setsid -w ssh -T admin@"$hostname" -- su - <<ANSWERS
$pass
sed -i 's/^\\(PermitRootLogin\\) no$/\\1 yes/g; /AuthorizedKeysFile \\/var\\/sshkeys/s/^/#/' /etc/ssh/sshd_config
systemctl restart sshd
exit \$?
ANSWERS

[[ $? == 0 ]] && ssh_deployPK ${hostname}
