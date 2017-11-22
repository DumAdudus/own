#!/bin/bash

declare -a region_list=('ap-northeast-1' 'ap-southeast-1')

jq_value()
{
    local content=$1
    local query=$2
    local ret_val
    ret_val=$(echo -n "$content" | jq "$query" -) || { echo 'Failed to query JSON value, exit!'; exit 1; }
    echo -n "$ret_val"
}

trim_quote()
{
    local ret_val
    ret_val=$(echo "$1" | tr -d '"')
    echo -n "$ret_val"
}

for r in "${region_list[@]}"; do
    json=$(aws --region "$r" ec2 describe-instances)
    instance=$(jq_value "$json" '.Reservations[].Instances[]|select(has("Tags"))|select(.Tags[].Key=="Name")')

    #inst_name=$(trim_quote "$(jq_value "$instance" '.Tags[]|select(.Key=="Name")|.Value')")
    #pub_ip=$(trim_quote "$(jq_value "$instance" '.PublicIpAddress')")
    inst_name=$(jq_value "$instance" '.Tags[]|select(.Key=="Name")|.Value')
    pub_ip=$(jq_value "$instance" '.PublicIpAddress')

    echo "$inst_name, $pub_ip"
done
