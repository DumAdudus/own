#!/bin/bash

declare -A BRANDS=(
    [umeng]="umeng"
    [tencent]="tencent*"
    [ali]="ali* amap"
    [bytedance]="byte* doubao douyin tiktok volcengine"
    [baidu]="baidu*"
    [jd]="jd"
    [google]="google* android blogspot fastlane firebase opensourceinsights v8 youtube"
    [facebook]="facebook*"
    [unity]="unity*"
)

construct_enimul() {
    local key
    key=$(awk -F'.' '{if(NF==2) {print "*" $0;} else {print $0;}}' | paste -sd ';' -)
    cat <<EOF
"$key": {
    "mode": "block"
},
EOF
}

filter_ads() {
    # local files=($(compgen -G "$1"))
    local files=(${1// / })
    if [ ${#files[@]} = 0 ]; then
        echo 'empty file list!'
        exit 1
    fi
    awk '!/^#/&&/ads/ {print $1}' "${files[@]}" | construct_enimul
}

stderr() {
    echo $@ >&2
}




for brand in "umeng" "tencent" "ali" "bytedance" "baidu" "jd" "google" "facebook" "unity"; do
    stderr "$brand ->"
    filter_ads "${BRANDS[$brand]}"
    stderr
done

stderr 'all ->'
awk '!/^#/&&!/include/&&!/^$/ {print}' category-ads | construct_enimul
