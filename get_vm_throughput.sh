#!/bin/bash -u

ss -tnlp
echo ''

which bc >/dev/null 2>&1 || sudo apt install bc

bytes2mega()
{
    local bytes=$1 mega
    mega=$(bc <<< "scale=2;$bytes/(1024*1024)")
    echo -n "${mega} MB"
}

nics=("$(ls -1 /sys/class/net/|grep -v lo)")

for nic in "${nics[@]}"; do
    rxb=$(cat "/sys/class/net/${nic}/statistics/rx_bytes")
    txb=$(cat "/sys/class/net/${nic}/statistics/tx_bytes")

    rxm=$(bytes2mega "$rxb")
    txm=$(bytes2mega "$txb")

    LC_ALL=C.UTF-8 echo -e "$nic:  \u21d1 $txm <-> \u21d3 $rxm\n"
done
