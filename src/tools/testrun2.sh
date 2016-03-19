#!/bin/bash

user="ladmin"
dir="p2psp/bin"

# Virtual Machine addresses
pc1="192.168.56.4"
pc2="192.168.58.5"
nat1="192.168.56.5"
nat2="192.168.58.4"
splitter="192.168.57.6"
server="192.168.57.7"
# NAT addresses towards the "internet"
nat1_pub="192.168.57.4"
nat2_pub="192.168.57.5"
local_source_addr=192.168.57.1
local_source_port=8080
src_channel="Big_Buck_Bunny_small.ogv"

set -e
function stop_processes() {
    set +e
    for host in $splitter $server $pc1 $pc2; do
        ssh $user@$host "pkill -f '$dir/splitter'"
        ssh $user@$host "pkill -f '$dir/peer'"
    done
}
# Register cleanup trap function
trap stop_processes EXIT

# Clear NAT mappings
#ssh "root@192.168.56.5" "conntrack -F" 2>/dev/null
#ssh "root@192.168.58.4" "conntrack -F" 2>/dev/null

ssh $user@$splitter unbuffer "$dir/splitter" --source_addr "$local_source_addr" \
    --source_port "$local_source_port" --channel "$src_channel" \
    --port "$splitter_port" --NTS --max_number_of_monitor_peers 2 \
    | sed -n -e 's_.*_\x1b[93mSplitter: \0\x1b[0m_p' &
sleep 3
ssh $user@$splitter unbuffer "$dir/peer" --splitter_addr "$splitter" \
    --splitter_port "$splitter_port" --port "$peer_port" --monitor \
    | sed -n -e 's_.*_\x1b[92mMonitor1: \0\x1b[0m_p' &
ssh $user@$server unbuffer "$dir/peer" --splitter_addr "$splitter" \
    --splitter_port "$splitter_port" --port "$peer_port" --monitor \
    | sed -n -e 's_.*_\x1b[96mMonitor2: \0\x1b[0m_p' &
ssh $user@$pc1 unbuffer "$dir/peer" --splitter_addr "$splitter" \
    --splitter_port "$splitter_port" --port "$peer_port" --port_step 1 \
    | sed -n -e 's_.*_\x1b[94mPeer1:    \0\x1b[0m_p' &
ssh $user@$pc2 unbuffer "$dir/peer" --splitter_addr "$splitter" \
    --splitter_port "$splitter_port" --port "$peer_port" --port_step 1 \
    | sed -n -e 's_.*_\x1b[95mPeer2:    \0\x1b[0m_p' &
sleep 2
vlc "http://$splitter:9999" --aout none 2>/dev/null &
id0=$!
sleep 2
vlc "http://$server:9999" --aout none 2>/dev/null &
id1=$!
sleep 2
vlc "http://$pc1:9999" --aout none 2>/dev/null &
id2=$!
sleep 2
vlc "http://$pc2:9999" --aout none 2>/dev/null &
id3=$!
sleep 20
set +e
kill $id0
kill $id1
kill $id2
kill $id3
stop_processes
# Show NAT mappings:
# Connection peer1 <-> peer2
echo "Peer1:"
ssh root@$nat1 conntrack -L -p udp 2>/dev/null | grep -e "dst=$nat2_pub" | grep -v UNREPLIED
# Connection peer2 <-> peer1
echo "Peer2:"
ssh root@$nat2 conntrack -L -p udp 2>/dev/null | grep -e "dst=$nat1_pub" | grep -v UNREPLIED
