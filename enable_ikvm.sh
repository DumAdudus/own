#!/bin/bash
set -u

scriptfolder=$(dirname "$(realpath "$0")")
. "${scriptfolder}/applib.sh"
. "${scriptfolder}/shlib.sh"

if [ ! $# -eq 1 ]; then
    read -r -p "Enter appliance host name: " appliance
else
    appliance=$1
fi

shortname=$(get_short_name "$appliance")
ipmihost=$(getipmihost "$shortname")
fqdn=$(getfqdn "$ipmihost")
uri="https://$fqdn"
urlv2="${uri}/cgi/login.cgi"

declare -A cookies

parse_cookie()
{
    # eliminate comments and blank lines
    c_no_h=$(echo -n "$1" | sed '/^$/d; /^# /d')
    readarray -t c_lines <<<"$(echo -n "$c_no_h")"
    for line in "${c_lines[@]}"; do
        read -r -a attr <<<"$(echo -n "$line")"
        cookies["${attr[5]}"]="${attr[6]}"
    done
}

enable_ikvm()
{
    cookie=$(${CURL} -c - --output /dev/null -X POST -d "name=${IPMI_USER}&pwd=${IPMI_PWD}&encodedpwd=$(echo -n "$IPMI_PWD" | base64)" "$urlv2")
    echo "$cookie"
    parse_cookie "$cookie"
    curl -vvk --cookie "SID=${cookies['SID']}" -H "X-Requested-With: XMLHttpRequest" \
        -d op=config_port \
        -d HTTP_PORT=80 \
        -d HTTPS_PORT=443 \
        -d IKVM_PORT=5900 \
        -d VM_PORT=623 \
        -d SSH_PORT=22 \
        -d WSMAN_PORT=5985 \
        -d SNMP_PORT=161 \
        -d HTTP_SERVICE=1 \
        -d HTTPS_SERVICE=1 \
        -d IKVM_SERVICE=1 \
        -d VM_SERVICE=1 \
        -d SSH_SERVICE=1 \
        -d SNMP_SERVICE=0 \
        -d WSMAN_SERVICE=0 \
        -d SSL_REDIRECT=1 \
        -d time_stamp="$(date)" \
        -d _= \
        "${uri}/cgi/op.cgi"
}

ipmiout()
{
    sleep 1
    ${CURL} --output /dev/null "${uri}/cgi/logout.cgi?SID=${cookies['SID']}"
}

enable_ikvm
ipmiout
