#!/bin/bash
# Lookups may not work for VPN / tun0
DEF_DNS='172.16.8.32'
BAK_DNS='172.16.8.2'
IP_LOOKUP="$(ip route get ${DEF_DNS} | awk '{ print $(NF-2); exit }')"  
IPv6_LOOKUP="$(ip -6 route get 2001:4860:4860::8888 | awk '{for(i=1;i<=NF;i++) if ($i=="src") print $(i+1)}')"  

# Just hard code these to your docker server's LAN IP if lookups aren't working
IP="${IP:-$IP_LOOKUP}"  # use $IP, if set, otherwise IP_LOOKUP
IPv6="${IPv6:-$IPv6_LOOKUP}"  # use $IPv6, if set, otherwise IP_LOOKUP

DOCKER_CONFIGS="$(dirname $(realpath $0))"
PASSWD='dumas'


echo "### Make sure your IPs are correct, hard code ServerIP ENV VARs if necessary\nIP: ${IP}\nIPv6: ${IPv6}"

# Default ports + daemonized docker container
docker run -d \
    --name pihole \
    -p 53:53/tcp -p 53:53/udp \
    -p 67:67/udp \
    -p 80:80 \
    -p 443:443 \
    -v "${DOCKER_CONFIGS}/pihole/:/etc/pihole/" \
    -v "${DOCKER_CONFIGS}/dnsmasq.d/:/etc/dnsmasq.d/" \
    -e ServerIP="${IP}" \
    -e DNS1="$DEF_DNS" \
    -e DNS2="$BAK_DNS" \
    -e WEBPASSWORD="$PASSWD" \
    --restart=unless-stopped \
    --cap-add=NET_ADMIN \
    --dns=${DEF_DNS} \
    pihole/pihole:latest
