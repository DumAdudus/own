#!/bin/bash
MAC='90:B1:1C:80:AD:92'
broadcast=255.255.255.255
port=9

dup_n_times()
{
    local str=$1
    local multi=$2

    echo -n "$(yes -- "$str" | head -$multi | tr -d '\n')"
}

wol_header=$(dup_n_times 'f' 12)
wol_mac=$(dup_n_times ${MAC//:/} 16)
wol_payload=$(xxd -r -p <<<"${wol_header}${wol_mac}")

sc_log_level=2
sc_param="-x -v $(dup_n_times '-d ' $sc_log_level)"
echo "$wol_payload" | socat $sc_param STDIO UDP4-DATAGRAM:$broadcast:$port,broadcast
#echo "$wol_payload" | socat $sc_param STDIN UDP4-DATAGRAM:$broadcast:$port,range=10.192.4.0/22
