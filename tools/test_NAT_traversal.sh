#!/bin/bash

# Configuration
nat_configs="rcn prcn sympp symsp symrp" # fcn not tested (results same as rcn)
user="ladmin"
dir="p2psp/src"
source_filename="Big_Buck_Bunny_small.ogv"
# As local source address you have to specify the local IP address of the host
# that is reachable by the virtual machines
local_source_addr=192.168.57.1
local_source_port=7000
peer_port=8000
splitter_port=9000
tmpdir="/tmp/p2psp_output"
testruns=20

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
    for host in $splitter $pc1 $pc2; do
        ssh "$user@$host" "pkill -f 'python2 -u $dir'" 2>/dev/null
    done
    kill $player0_id 2>/dev/null
    kill $player1_id 2>/dev/null
    kill $player2_id 2>/dev/null
    set -e
}
function stop_source() {
    set +e
    kill $source_id 2>/dev/null
    set -e
}
function stop_processes_all() {
    stop_processes
    stop_source
}
# Register cleanup trap function
trap stop_processes_all EXIT

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

# Clear NAT entries
ssh "root@$nat1" conntrack -F 2>/dev/null
ssh "root@$nat2" conntrack -F 2>/dev/null

# Create table
result="Peer1\2	"
for nat in $nat_configs; do
    result="$result| $nat	"
done
result="$result
========"
for nat in $nat_configs; do
    result="$result========"
done

# Run test
for nat1_config in $nat_configs; do
    result="$result
$nat1_config "
    ssh "root@$nat1" iptables-restore /etc/iptables/iptables.rules.${nat1_config}1
    for nat2_config in $nat_configs; do
        echo "Configuring NATs: $nat1_config <-> $nat2_config."
        ssh "root@$nat2" iptables-restore /etc/iptables/iptables.rules.${nat2_config}2

        # Run stream source
        cvlc --sout "#duplicate{dst=standard{mux=ogg,dst=:$local_source_port,access=http}}" \
            "$source_filename" 2>/dev/null &
        source_id=$!
        sleep 0.5

        successes=0
        date

        for testrun in $(seq $testruns); do

            # Run splitter
            splitter_output="$tmpdir/$nat1_config.$nat2_config.splitter.txt"
            ssh "$user@$splitter" python2 -u "$dir/splitter.py" --source_addr "$local_source_addr" \
                --source_port "$local_source_port" --port "$splitter_port" >"$splitter_output" &

            # Build output filenames
            monitor_output="$tmpdir/$nat1_config.$nat2_config.monitor.txt"
            peer1_output="$tmpdir/$nat1_config.$nat2_config.peer1.txt"
            peer2_output="$tmpdir/$nat1_config.$nat2_config.peer2.txt"

            # Run monitor on same host as splitter
            peer_cmd="python2 -u $dir/peer.py --splitter_addr '$splitter' \
                --splitter_port '$splitter_port' --port '$peer_port' --port_step 2 | sed 's_[^m]*m__g'"
            ssh "$user@$splitter" "$peer_cmd" >"$monitor_output" &

            # Run peers
            ssh "$user@$pc1" "$peer_cmd" >"$peer1_output" &
            ssh "$user@$pc2" "$peer_cmd" >"$peer2_output" &

            # Clear NAT entries
            ssh "root@$nat1" "conntrack -F" 2>/dev/null
            ssh "root@$nat2" "conntrack -F" 2>/dev/null
            sleep 1

            # Run players
            cvlc "http://$splitter:9999" --vout none --aout none 2>/dev/null >/dev/null &
            player0_id=$!
            sleep 0.5
            cvlc "http://$pc1:9999" --vout none --aout none 2>/dev/null >/dev/null &
            player1_id=$!
            sleep 0.5
            cvlc "http://$pc2:9999" --vout none --aout none 2>/dev/null >/dev/null &
            player2_id=$!

            # Wait until connections are established
            sleep 5
            # Stop the test
            stop_processes

            # Get outputs; the exit value is determined by "grep" and will be "0"
            # if a peer received messages from both other peers
            set +e
            success=""
            peer1_conn="$(ssh root@$nat1 conntrack -L -p udp 2>/dev/null | grep -v UNREPLIED)"
            peer2_conn="$(ssh root@$nat2 conntrack -L -p udp 2>/dev/null | grep -v UNREPLIED)"
            # Connection peer1 <-> splitter
            <<<"$peer1_conn" grep -e "src=$splitter dst=$nat1_pub sport=$splitter_port" >/dev/null
            success="$success$?"
            # Connection peer1 <-> monitor
            <<<"$peer1_conn" grep -e "src=$splitter dst=$nat1_pub sport=$peer_port" >/dev/null
            success="$success$?"
            # Connection peer1 <-> peer2
            <<<"$peer1_conn" grep -e "dst=$nat2_pub sport=$peer_port" >/dev/null
            success="$success$?"
            # Connection peer2 <-> splitter
            <<<"$peer2_conn" grep -e "src=$splitter dst=$nat2_pub sport=$splitter_port" >/dev/null
            success="$success|$?"
            # Connection peer2 <-> monitor
            <<<"$peer2_conn" grep -e "src=$splitter dst=$nat2_pub sport=$peer_port" >/dev/null
            success="$success$?"
            # Connection peer2 <-> peer1
            <<<"$peer2_conn" grep -e "dst=$nat1_pub sport=$peer_port" >/dev/null
            success="$success$?"
            set -e

            if [ "$success" == "000|000" ]; then
                successes=$((successes+1))
            fi
            echo -ne "\rSuccessful runs: $successes | $testrun"

            # Increment ports
            splitter_port=$((splitter_port+1))
            peer_port=$((peer_port+1))

        done

        # Append to result table
        result="$result	| $((successes*100/$testruns)) "

        stop_source
        # Increment port of the source
        local_source_port=$((local_source_port+1))

        # Print result table
        echo; echo
        echo "$result"
        echo
    done
done

# Clear trap
trap - EXIT

# Print result table
echo
echo "$configuration:"
echo "Results in % ($testruns test runs):"
echo
echo "$result"
echo
