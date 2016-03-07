#!/bin/bash

# Configuration
nat_configs="fcn rcn prcn sympp symsp symrp"
user="ladmin"
dir="p2psp/src"
source_filename="Big_Buck_Bunny_small.ogv"
# As local source address you have to specify the local IP address of the host
# that is reachable by the virtual machines
local_source_addr=192.168.57.1
sequential_runs=5
parallel_runs=10
testruns=$((sequential_runs*parallel_runs))
local_source_port=7000
peer_port=8000
splitter_port=$((peer_port+(parallel_runs*testruns)))

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
        ssh "$user@$host" "pkill -f 'python3 -u $dir'" 2>/dev/null
    done
    killall vlc 2>/dev/null
    killall netcat 2>/dev/null
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

        # Clear NAT entries
        ssh "root@$nat1" conntrack -F 2>/dev/null
        ssh "root@$nat2" conntrack -F 2>/dev/null

        successes=0

        run_single_test(){
            # parameters: splitter_port, peer_port, player_port

            # Run splitter
            ssh "$user@$splitter" python3 -u "$dir/splitter.py" --NTS --source_addr "$local_source_addr" \
                --source_port "$local_source_port" --channel "$source_filename" --port "$splitter_port" >/dev/null &

            # Run monitor on same host as splitter
            peer_cmd="python3 -u $dir/peer.py --splitter_addr '$splitter' --player_port '$3' \
                --splitter_port '$1' --port '$2' | sed 's_[^m]*m__g'"
            peer_cmd_symsp="python3 -u $dir/peer.py --splitter_addr '$splitter' --player_port '$3' \
                --splitter_port '$1' --port '$2' --port_step 1 | sed 's_[^m]*m__g'"
            ssh "$user@$splitter" "$peer_cmd" >/dev/null &

            # Run peers
            if [ "$nat1_config" == "symsp" ]; then
                ssh "$user@$pc1" "$peer_cmd_symsp" >/dev/null &
            else
                ssh "$user@$pc1" "$peer_cmd" >/dev/null &
            fi
            if [ "$nat2_config" == "symsp" ]; then
                ssh "$user@$pc2" "$peer_cmd_symsp" >/dev/null &
            else
                ssh "$user@$pc2" "$peer_cmd" >/dev/null &
            fi
            sleep 1

            # Run players
            netcat "$splitter" "$3" 2>/dev/null >/dev/null &
            sleep 1
            netcat "$pc1" "$3" 2>/dev/null >/dev/null &
            sleep 1
            netcat "$pc2" "$3" 2>/dev/null >/dev/null &

            # Get outputs; the exit value is determined by "grep" and will be "0"
            # if a peer received messages from both other peers
            set +e
            wait $!
        }

        for sequential_run in $(seq $sequential_runs); do
            date
            # Run stream source
            cvlc --sout "#duplicate{dst=standard{mux=ogg,dst=:/$source_filename,access=http}}" \
                "$source_filename" --http-port "$local_source_port" 2>/dev/null &
            sleep 1
            player_port=$((splitter_port+(parallel_runs*testruns)))
            for parallel_run in $(seq $parallel_runs); do
                run_single_test $splitter_port $peer_port $player_port &
                sleep 0.5
                # Increment ports by $parallel_runs to avoid conflict between parallel runs
                splitter_port=$((splitter_port+parallel_runs))
                peer_port=$((peer_port+parallel_runs))
                player_port=$((player_port+1))
            done
            # Wait until connections are established
            sleep 35
            # Stop the test
            stop_processes
            # Gather results
            set +e
            peer1_conn="$(ssh root@$nat1 conntrack -L -p udp 2>/dev/null | grep -v UNREPLIED)"
            peer2_conn="$(ssh root@$nat2 conntrack -L -p udp 2>/dev/null | grep -v UNREPLIED)"
            # Reset ports
            splitter_port=$((splitter_port-parallel_runs*parallel_runs))
            peer_port=$((peer_port-parallel_runs*parallel_runs))
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
                splitter_port=$((splitter_port+parallel_runs))
                peer_port=$((peer_port+parallel_runs))
            done
            set -e
            echo "Successful runs: $successes | $((sequential_run*parallel_runs))"
            # Reset ports for next test run
            splitter_port=$((splitter_port+1-parallel_runs*parallel_runs))
            peer_port=$((peer_port+1-parallel_runs*parallel_runs))
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
