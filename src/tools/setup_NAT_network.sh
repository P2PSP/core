#!/bin/bash

NAMESPACES="pc1 nat1 splitter server nat2 pc2"
BRIDGES="brnet1 brinet brnet2"

# Namespace addresses
pc1="192.168.56.4"
pc2="192.168.58.5"
nat1="192.168.56.5"
nat2="192.168.58.4"
splitter="192.168.57.6"
server="192.168.57.7"
# NAT addresses towards the "internet"
nat1_pub="192.168.57.4"
nat2_pub="192.168.57.5"



set -e
echo "Creating namespaces and interfaces"

# Create namespaces
for NAMESPACE in $NAMESPACES; do
    ip netns add $NAMESPACE
    # Enable loopback device
    ip netns exec $NAMESPACE ip link set dev lo up
done

# Create bridges
for BRIDGE in $BRIDGES; do
    brctl addbr $BRIDGE
    brctl stp $BRIDGE off
    ip link set dev $BRIDGE up
done

create_interface_to_bridge(){
    NAMESPACE=$1
    INTERFACE=$2
    ADDRESS=$3
    BRIDGE=$4

    # Create veth pair
    ip link add $INTERFACE type veth peer name $INTERFACE-br
    # Attach to bridge
    brctl addif $BRIDGE $INTERFACE-br
    # Attach to the namespace
    ip link set $INTERFACE netns $NAMESPACE
    # Activate interfaces and set addresses
    ip netns exec $NAMESPACE ifconfig $INTERFACE $ADDRESS up
    ip link set dev $INTERFACE-br up
}

# Add interfaces to internet
create_interface_to_bridge pc1 ifpc1 $pc1 brnet1
create_interface_to_bridge nat1 ifnat11 $nat1 brnet1
create_interface_to_bridge nat1 ifnat12 $nat1_pub brinet
create_interface_to_bridge splitter ifsplitter $splitter brinet
create_interface_to_bridge server ifserver $server brinet
create_interface_to_bridge nat2 ifnat21 $nat2_pub brinet
create_interface_to_bridge nat2 ifnat22 $nat2 brnet2
create_interface_to_bridge pc2 ifpc2 $pc2 brnet2

# Set bridge addresses
ifconfig brnet1 192.168.56.1 up
ifconfig brinet 192.168.57.1 up
ifconfig brnet2 192.168.58.1 up
# Configure routing
ip netns exec pc1 ip route add default via 192.168.56.5
ip netns exec pc2 ip route add default via 192.168.58.4
for NAMESPACE in nat1 splitter server nat2; do
    ip netns exec $NAMESPACE ip route add default via 192.168.57.1
done

# Run sshd
for NAMESPACE in $NAMESPACES; do
    ip netns exec $NAMESPACE /usr/bin/sshd
done

# Configure packet forwarding
ip netns exec nat1 sysctl net.ipv4.ip_forward=1
ip netns exec nat2 sysctl net.ipv4.ip_forward=1
# Initial NAT settings
ip netns exec nat1 iptables-restore /etc/iptables/iptables.rules.prcn1
ip netns exec nat2 iptables-restore /etc/iptables/iptables.rules.prcn2
