#!/bin/bash

NAMESPACES="pc1 nat1 splitter server nat2 pc2"
BRIDGES="brnet1 brinet brnet2"

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
