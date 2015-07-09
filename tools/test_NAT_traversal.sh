#!/bin/bash

# Configuration
nat_configs="fcn rcn prcn symsp sympp symrp"
user="ladmin"
dir="p2psp/src"
source_filename="Big_Buck_Bunny_small.ogv"
# As local source address you have to specify the local IP address of the host
# that is reachable by the virtual machines
local_source_addr=192.168.57.1
local_source_port=8080
peer_port=8100
splitter_port=8200
tmpdir="/tmp/p2psp_output"

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
    echo "Stopping splitter, peers and players."
    for host in $pc1 $pc2 $splitter; do
        ssh "$user@$host" killall python2 2>/dev/null
    done
    kill $player0_id 2>/dev/null
    kill $player1_id 2>/dev/null
    kill $player2_id 2>/dev/null
    set -e
}
function cleanup() {
    stop_processes
    echo "Stopping source."
    kill $source_id 2>/dev/null
}
# Register cleanup trap function
trap cleanup EXIT

# Exit on error
set -e

# Clean output directory
rm -rf "$tmpdir"
mkdir -p "$tmpdir"

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

# Start the source
echo "Starting source."
cvlc "$source_filename" --sout "#duplicate{dst=standard{mux=ogg,dst=,access=http}}" |& grep error &
source_id=$!

# Create table
result="Peer1\2	"
for nat in $nat_configs; do
    result="$result| $nat	"
done
result="$result
========================================================"

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
        splitter_output="$tmpdir/$nat1_config.$nat2_config.splitter.txt"
        ssh "$user@$splitter" python2 "$dir/splitter.py" --source_addr "$local_source_addr" \
            --source_port "$local_source_port" --port "$splitter_port" >"$splitter_output" &

        # Build output filenames
        monitor_output="$tmpdir/$nat1_config.$nat2_config.monitor.txt"
        peer1_output="$tmpdir/$nat1_config.$nat2_config.peer1.txt"
        peer2_output="$tmpdir/$nat1_config.$nat2_config.peer2.txt"

        # Run monitor on same host as splitter
        peer_cmd="python2 -u $dir/peer.py --splitter_addr '$splitter' \
            --splitter_port '$splitter_port' --port '$peer_port' | sed 's_[^m]*m__g'"
        ssh "$user@$splitter" "$peer_cmd" >"$monitor_output" &

        # Run peers
        ssh "$user@$pc1" "$peer_cmd" >"$peer1_output" &
        ssh "$user@$pc2" "$peer_cmd" >"$peer2_output" &

        # Run players
        echo "Running players without any output."
        sleep 3
        cvlc "http://$splitter:9999" --vout none --aout none 2>/dev/null >/dev/null &
        player0_id=$!
        sleep 1
        cvlc "http://$pc1:9999" --vout none --aout none 2>/dev/null >/dev/null &
        player1_id=$!
        sleep 1
        cvlc "http://$pc2:9999" --vout none --aout none 2>/dev/null >/dev/null &
        player2_id=$!

        # Wait until stream is buffered
        sleep 12
        # Stop the test
        stop_processes

        splitter_grep="Received a message from ('$splitter', $splitter_port)"
        monitor_grep="Received a message from ('$splitter"
        peer1_grep="Received a message from ('$nat1_pub"
        peer2_grep="Received a message from ('$nat2_pub"
        # Get outputs; the exit value is determined by "grep" and will be "0"
        # if a peer received messages from both other peers
        # Todo: also check if peers received messages from the splitter
        set +e
        success=""
        grep "$monitor_output" -e "$splitter_grep" >/dev/null
        success="$success$?"
        grep "$monitor_output" -e "$peer1_grep" >/dev/null
        success="$success$?"
        grep "$monitor_output" -e "$peer2_grep" >/dev/null
        success="$success$?"
        grep "$peer1_output" -e "$splitter_grep" >/dev/null
        success="$success|$?"
        grep "$peer1_output" -e "$monitor_grep" >/dev/null
        success="$success$?"
        grep "$peer1_output" -e "$peer2_grep" >/dev/null
        success="$success$?"
        grep "$peer2_output" -e "$splitter_grep" >/dev/null
        success="$success|$?"
        grep "$peer2_output" -e "$monitor_grep" >/dev/null
        success="$success$?"
        grep "$peer2_output" -e "$peer1_grep" >/dev/null
        success="$success$?"
        set -e
        echo "Result (mon|peer1|peer2, 000=success): $success"

        # Append to result table
        if [ "$success" == "000|000|000" ]; then
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
