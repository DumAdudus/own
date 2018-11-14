#!/bin/bash
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

load_file=${shortname}.jnlp
uri="https://$fqdn"

usev1=1
urlv1="${uri/s/}/rpc/WEBSES/create.asp"
urlv2="${uri}/cgi/login.cgi"

ipmiv1()
{
    echo 'Using v1 protocol'
    raw_cookie=$(${CURL} -d "WEBVAR_USERNAME=${IPMI_USER}&WEBVAR_PASSWORD=${IPMI_PWD}" "$urlv1")
    echo "$raw_cookie"
    cookie=$(echo -n "$raw_cookie" | awk -F\' '/SESSION_COOKIE/{print $4}')
    ${CURL} --cookie "SessionCookie=${cookie}" "${uri}/Java/jviewer.jnlp" -o "${load_file}"
}

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

ipmiv2()
{
    echo 'Using v2 protocol'
    cookie=$(${CURL} -c - --output /dev/null -X POST -d "name=${IPMI_USER}&pwd=${IPMI_PWD}&encodedpwd=$(echo -n ${IPMI_PWD} | base64)" "$urlv2")
    echo "$cookie"
    parse_cookie "$cookie"
    ${CURL} --cookie "SID=${cookies['SID']}" "${uri}/cgi/url_redirect.cgi?url_name=sess_04&url_type=jwsk&lang_setting=English" -o "${load_file}"
}

isnum()
{
    re='^[0-9]+$'
    [[ "$1" =~ $re ]] && return 0 || return 1
}

waitproc()
{
    local pid=$1
    while [ -e "/proc/$pid" ]; do sleep 0.5; done
}

ipmiout()
{
    if [[ $usev1 != 1 ]]; then
        sleep 1
        local pid
        pid=$(pgrep -f "${load_file}")
        if isnum "$pid"; then waitproc "$pid"; fi
        ${CURL} --output /dev/null "${uri}/cgi/logout.cgi?SID=${cookies['SID']}"
    fi
}

add_sec_except()
{
    local ipmi_ip=
    local java_sec_folder="$HOME/.java/deployment/security"
    local sec_file="$java_sec_folder/exception.sites"
    [ ! -d "$java_sec_folder" ] && mkdir -p "$java_sec_folder"
    ipmi_ip=$(hostname2ip "$ipmihost")
    for item in "$uri" "https://$ipmi_ip"; do
        grep -F -qs "$item" "$sec_file" || { echo "Update Java security exception.sites: $item"; echo "$item" >> "$sec_file"; }
    done
}

http_code=$(${CURL} -Sf "$urlv1" --write-out '%{http_code}' --output /dev/null)

if [[ ${http_code} == 200 ]]; then
    ipmiv1
else
    usev1=0
    ipmiv2
fi

add_sec_except
{ javaws -Xnosplash "${load_file}" &> /dev/null; ipmiout; } & disown
