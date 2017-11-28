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
    rxb=$(cat /sys/class/net/eth0/statistics/rx_bytes)
    txb=$(cat /sys/class/net/eth0/statistics/tx_bytes)

    rxm=$(bytes2mega "$rxb")
    txm=$(bytes2mega "$txb")

    echo "$nic  >  tx: $txm      rx: $rxm"
done
