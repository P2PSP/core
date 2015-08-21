#!/bin/bash

# This script runs whole teams and quits them after a while,
# filtering and colorizing the output messages.
# It automatically increases port numbers to avoid reusing NAT mappings.

# This script has to be sourced by `source testrun.sh`
# so that environment variables can be set.
# The NAT types have to be set with set_NAT_config.sh before running tests.

if [ -z "$type" ]; then
    peer_port=1600
    splitter_port=2600
else
    splitter_port=$((splitter_port+1))
    peer_port=$((peer_port+1))

    export splitter_port
    export peer_port

    ./testrun2.sh
    # Record a testrun:
    # asciinema rec -c ./testrun2.sh asciinema.txt
fi
