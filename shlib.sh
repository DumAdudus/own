#!/bin/bash

SSH="ssh -24"

_shlib_init()
{
    local sshcfg="$(dirname "$(readlink -f "$1")")/ssh_config"
    [ -f "${sshcfg}" ] && SSH="$SSH -F $sshcfg"
}

sed_escape_backslash()
{
    echo $1 | sed -e 's/[\/&]/\\&/g'
}

ssh_getHostname()
{
    #${SSH} -o 'ProxyCommand=echo %h>&2' $1 2>&1 | fgrep -v 'ssh_exchange_identification'
    ${SSH} -G $1 | grep -Po '^hostname \K.+'
}

ssh_refreshHostKey()
{
    local host_name=$1
    local ssh_opts="-o StrictHostKeyChecking=no -o BatchMode=yes"
    ${SSH} $ssh_opts ${host_name} exit |& grep -qF 'IDENTIFICATION HAS CHANGED'

    if [ $? -eq 0 ]; then
        ssh-keygen -R ${host_name}
        ${SSH} -q $ssh_opts ${host_name} exit
    fi
}

ssh_deployPK()
{
    local host_name=$1
    /usr/bin/expect -c "
        set timeout 120
        spawn ssh-copy-id root@${host_name}
        expect \"password: \" { send \"P@ssw0rd\r\" }
        expect \"wanted were added.\" { exit 0 }"
}

ssh_isAlias()
{
    local host_name=$(ssh_getHostname $1)
    [ "$host_name" = "$1" ] && return 1 || return 0
}


hostname2ip()
{
    local -r EPIC_DNS='172.16.8.2'
    local box_info=($(host -tA $1 $EPIC_DNS | grep 'has' | head -n 1 | cut -d' ' -f1,4; exit ${PIPESTATUS[0]}))
    local ip=${box_info[1]}
    echo -n $ip
}

_shlib_init $0
