#!/bin/bash

SSH="ssh -24"

_shlib_init()
{
    local sshcfg="$(dirname "$(realpath "$1")")/ssh_config"
    [ -f "${sshcfg}" ] && SSH="$SSH -F $sshcfg"
}

sed_escape_backslash()
{
    echo "$1" | sed -e 's/[\/&]/\\&/g'
}

ssh_alias2hostname()
{
    ${SSH} -G "$1" | awk '/^hostname /{print $2}'
}

ssh_refreshHostKey()
{
    local host_name=$1
    local ssh_opts="-o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=2"
    if ! ${SSH} $ssh_opts "$host_name" exit |& grep -qF 'IDENTIFICATION HAS CHANGED'; then
        ssh-keygen -R "$host_name"
        ${SSH} -q $ssh_opts "$host_name" exit
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

_shlib_init "$0"
