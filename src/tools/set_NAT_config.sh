#!/bin/bash

nat1="192.168.56.5"
nat2="192.168.58.4"

[ "$#" == "2" ] || (echo "Usage: $0 [type of NAT 1] [type of NAT 2]"; exit 1)

ssh "root@$nat1" iptables-restore /etc/iptables/iptables.rules.${1}1
ssh "root@$nat2" iptables-restore /etc/iptables/iptables.rules.${2}2
