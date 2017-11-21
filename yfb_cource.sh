#!/bin/bash

FFMPEG='ffmpeg -hide_banner -v info'
yfb_cookie=yfb_cookie.txt
CURL="curl -s -b ${yfb_cookie}"
aes_key_regex='http://edu.yanfabu.com/hls/[0-9]*/clef/[^"]*'
py_codes="import json,sys; l=json.load(sys.stdin); print l['title']+'\\n'+l['mediaHLSUri']+'\\n'+l['mediaId']"
course_id=1165


exit_on_error()
{
    echo "$1, exit!"
    exit 1
}

get_lesson()
{
    local lesson_id lesson_url
    lesson_id=$1
    lesson_url=$(printf "http://edu.yanfabu.com/course/%s/lesson/%s" "$course_id" "$lesson_id")

    local raw title hls_url media_id
    readarray -t raw <<<"$(${CURL} "$lesson_url" | PYTHONIOENCODING=utf8 python -c "$py_codes")"
    [[ ${#raw[@]} != 3 ]] && exit_on_error "Wrong info got ${raw[*]}, exit!"
    title=${raw[0]}
    hls_url=$(${CURL} "${raw[1]}" | tail -1; exit "${PIPESTATUS[0]}") || exit_on_error 'Cannot fetch HLS list'
    media_id=${raw[2]}

    local local_hls aes_key key_url
    local_hls="${title}.m3u8"
    aes_key="${media_id}.key"

    ${CURL} "$hls_url" -o "$local_hls" || exit_on_error 'Cannot fetch HLS media'
    key_url=$(grep -Po "$aes_key_regex" "$local_hls" | head -1) || exit_on_error 'Failed finding AES key URL'
    ${CURL} "$key_url" -o "$aes_key" || exit_on_error 'Failed fetching AES key'
    sed -i -e "s@${aes_key_regex}@${media_id}\\.key@g" "$local_hls"
    ${FFMPEG} -i "$local_hls" -bsf:a aac_adtstoasc -c copy "${title}.mp4"
}

main()
{
    local course_id=1165
    local lesson_id_start=6192 lesson_id_end=6207
    local lesson_id_start=6194 lesson_id_end=6194
    for id in $(seq ${lesson_id_start} ${lesson_id_end}); do
        get_lesson "$id" || exit 1
    done
}

main

