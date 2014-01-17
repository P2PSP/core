#!/bin/sh

#set -x

./run_source_480.sh -l 4554 -s "localhost:4551" &

peer_port=10001

./run_peer_480.sh -s "localhost:4554" -l 10001 &
