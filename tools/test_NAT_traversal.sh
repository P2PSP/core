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
sequential_runs=5
parallel_runs=10
testruns=$((sequential_runs*parallel_runs))

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
    killall vlc 2>/dev/null
    set -e
}
# Register cleanup trap function
trap stop_processes EXIT

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

        successes=0

        run_single_test(){
            # parameters: splitter_port, peer_port, player_port

            # Run splitter
            splitter_output="$tmpdir/$nat1_config.$nat2_config.$1.splitter.txt"
            ssh "$user@$splitter" python2 -u "$dir/splitter.py" --source_addr "$local_source_addr" \
                --source_port "$local_source_port" --port "$splitter_port" >"$splitter_output" &

            # Build output filenames
            monitor_output="$tmpdir/$nat1_config.$nat2_config.$1.monitor.txt"
            peer1_output="$tmpdir/$nat1_config.$nat2_config.$1.peer1.txt"
            peer2_output="$tmpdir/$nat1_config.$nat2_config.$1.peer2.txt"

            # Run monitor on same host as splitter
            peer_cmd="python2 -u $dir/peer.py --splitter_addr '$splitter' --player_port '$3' \
                --splitter_port '$1' --port '$2' --port_step 1 | sed 's_[^m]*m__g'"
            ssh "$user@$splitter" "$peer_cmd" >"$monitor_output" &

            # Run peers
            ssh "$user@$pc1" "$peer_cmd" >"$peer1_output" &
            ssh "$user@$pc2" "$peer_cmd" >"$peer2_output" &
            sleep 1

            # Run players
            cvlc "http://$splitter:$3" --vout none --aout none 2>/dev/null >/dev/null &
            sleep 1
            cvlc "http://$pc1:$3" --vout none --aout none 2>/dev/null >/dev/null &
            sleep 1
            cvlc "http://$pc2:$3" --vout none --aout none 2>/dev/null >/dev/null &

            # Get outputs; the exit value is determined by "grep" and will be "0"
            # if a peer received messages from both other peers
            set +e
            wait $!
        }

        for sequential_run in $(seq $sequential_runs); do
            date
            # Run stream source
            cvlc --sout "#duplicate{dst=standard{mux=ogg,dst=:$local_source_port,access=http}}" \
                "$source_filename" 2>/dev/null &
            sleep 1
            player_port=10000
            for parallel_run in $(seq $parallel_runs); do
                run_single_test $splitter_port $peer_port $player_port &
                sleep 0.5
                # Increment ports by 100 to avoid conflict between parallel runs
                splitter_port=$((splitter_port+100))
                peer_port=$((peer_port+100))
                player_port=$((player_port+1))
            done
            # Wait until connections are established
            sleep 22
            # Stop the test
            stop_processes
            # Gather results
            set +e
            peer1_conn="$(ssh root@$nat1 conntrack -L -p udp 2>/dev/null | grep -v UNREPLIED)"
            peer2_conn="$(ssh root@$nat2 conntrack -L -p udp 2>/dev/null | grep -v UNREPLIED)"
            # Reset ports
            splitter_port=$((splitter_port-100*parallel_runs))
            peer_port=$((peer_port-100*parallel_runs))
            for parallel_run in $(seq $parallel_runs); do
                success=""
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
                echo $success
                if [ "$success" == "000|000" ]; then
                    successes=$((successes+1))
                fi
                # Increment ports
                splitter_port=$((splitter_port+100))
                peer_port=$((peer_port+100))
            done
            set -e
            echo "Successful runs: $successes | $((sequential_run*parallel_runs))"
            # Reset ports for next test run
            splitter_port=$((splitter_port+1-100*parallel_runs))
            peer_port=$((peer_port+1-100*parallel_runs))
            local_source_port=$((local_source_port+1))
        done

        # Append to result table
        result="$result	| $((successes*100/(sequential_runs*parallel_runs))) "

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
