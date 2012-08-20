#!/bin/sh

#set -x

./run_source_480.sh -s 4554 -i "localhost:4551" &

peer_port=9999

./run_peer_480.sh -s "localhost:4554" -l $peer_port &
