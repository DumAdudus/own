#!/bin/bash
IPV4SUB='100.127.0.0/24'
IPV6SUB='2001:db8:2::/64'
DOCKER_NET='pool'
DOCKER_VOL='knot-cfg'
KNOT_IP='100.127.0.2'
DNS_IP='11.53.53.52'
IMAGE='cznic/knot-resolver:6'

docker pull $IMAGE
docker network create --subnet=$IPV4SUB --ipv6 --subnet $IPV6SUB $DOCKER_NET
docker volume create -o type=none -o o=bind -o device=/root/knot-resolver $DOCKER_VOL
docker run -d --name knot-resolver --restart=unless-stopped --net $DOCKER_NET --ip $KNOT_IP -v $DOCKER_VOL:/etc/knot-resolver:ro -p 127.0.0.1:5533:53/udp $IMAGE
#iptables -t nat -A OUTPUT -p udp -d $DNS_IP --dport 53 -j DNAT --to-destination $KNOT_IP
