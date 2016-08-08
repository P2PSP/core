#!/bin/bash

NAMESPACES="pc1 nat1 splitter monitor pc2"
BRIDGES="localNet publicNet"

# Cleanup
echo "Cleaning up"
killall sshd
pkill -f 'python3 -u'
for NAMESPACE in $NAMESPACES; do
    ip netns delete $NAMESPACE
done
for BRIDGE in $BRIDGES; do
    ip link set dev $BRIDGE down
    brctl delbr $BRIDGE
done
