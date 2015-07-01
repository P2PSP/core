#!/bin/bash

# Configuration
nat_configs="fcn rcn prcn sym"
user="ladmin"
dir="p2psp/src"
source_addr=150.214.150.68
channel=BBB-134.ogv
source_port=4551
peer_port=8100
splitter_port=9100

# Virtual Machine addresses
pc1="192.168.56.4"
pc2="192.168.58.5"
nat1="192.168.56.5"
nat2="192.168.58.4"
splitter="192.168.57.6"
# NAT addresses towards the "internet"
nat1_pub="192.168.57.4"
nat2_pub="192.168.57.5"

function stop_processes() {
    set +e
    echo "Stopping splitter, peers, players and source."
    for host in $pc1 $pc2 $splitter; do
        ssh "$user@$host" killall python2 2>/dev/null
    done
    kill $player1_id 2>/dev/null
    kill $player2_id 2>/dev/null
    kill $source_id 2>/dev/null
    set -e
}
# Register cleanup trap function
trap stop_processes EXIT

# Exit on error
set -e

# Get P2PSP configuration from code
splitter_class="$(ssh $user@$splitter cat $dir/splitter.py \
    | sed -n "s/.* splitter = \(Splitter_...\)(.*/\1/p" | tail -n1)"
monitor_class="$(ssh $user@$pc1 cat $dir/peer.py \
    | sed -n "s/.* peer = \(Monitor_...\)(.*/\1/p" | tail -n1)"
peer_class="$(ssh $user@$pc2 cat $dir/peer.py \
    | sed -n "s/.* peer = \(Peer_...\)(.*/\1/p" | tail -n1)"
branch="$(ssh $user@$pc1 cd $dir \; git rev-parse --abbrev-ref HEAD)"
commit="$(ssh $user@$pc1 cd $dir \; git rev-parse --short HEAD)"
configuration="$splitter_class, $monitor_class, $peer_class (branch $branch, commit $commit)"
echo "Configuration: $configuration"
echo

# Create table
result="Mon\Peer"
for nat in $nat_configs; do
    result="$result| $nat	"
done
result="$result
======================================"

# Run test
for nat1_config in $nat_configs; do
    result="$result
$nat1_config "
    ssh "root@$nat1" iptables-restore /etc/iptables/empty.rules \; \
        iptables -F \; \
        iptables -X \; \
        iptables -t nat -F \; \
        iptables -t nat -X \; \
        iptables-restore /etc/iptables/iptables.rules.${nat1_config}
    for nat2_config in $nat_configs; do
        echo "Configuring NATs: $nat1_config <-> $nat2_config."
        ssh "root@$nat2" iptables-restore /etc/iptables/empty.rules \; \
            iptables -F \; \
            iptables -X \; \
            iptables -t nat -F \; \
            iptables -t nat -X \; \
            iptables-restore /etc/iptables/iptables.rules.${nat2_config}

        echo "Running splitter and peers."
        # Run splitter
        ssh "$user@$splitter" python2 "$dir/splitter.py" --source_addr "$source_addr" \
            --source_port "$source_port" --channel "$channel" --port "$splitter_port" >/dev/null &
        splitter_id=$!

        # Run peers
        peer_cmd="python2 -u $dir/peer.py --splitter_addr '$splitter' \
            --splitter_port '$splitter_port' --port '$peer_port'"
        # The exit value is determined by "grep" and will be "0" if
        # peer1 received messages from peer2 and vice versa
        ssh "$user@$pc1" "$peer_cmd | sort -u | grep \"Received a message from ('$nat2_pub\"" >/dev/null &
        peer1_id=$!
        ssh "$user@$pc2" "$peer_cmd | sort -u | grep \"Received a message from ('$nat1_pub\"" >/dev/null &
        peer2_id=$!

        # Run players
        echo "Running players."
        sleep 3
        cvlc "http://$pc1:9999" --vout none 2>/dev/null >/dev/null &
        player1_id=$!
        sleep 1
        cvlc "http://$pc2:9999" --vout none 2>/dev/null >/dev/null &
        player2_id=$!

        # Wait until stream is buffered
        sleep 12
        # Stop the test
        stop_processes

        # Get outputs
        set +e
        wait $peer1_id
        peer1_success=$?
        wait $peer2_id
        peer2_success=$?
        set -e

        # Append to result table
        if [ "$peer1_success" == "0" ] && [ "$peer2_success" == "0" ]; then
            success=yes
        else
            success=no
        fi
        echo "Success: $success"
        result="$result	| $success"

        # Increment ports
        splitter_port=$((splitter_port+1))
        peer_port=$((peer_port+1))

        # Print result table
        echo
        echo "$result"
        echo
    done
done

# Clear trap
trap - EXIT

# Print result table
echo
echo "$configuration:"
echo
echo "$result"
echo
