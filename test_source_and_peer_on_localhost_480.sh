./run_oggfwd_480.sh &
./run_source_480.sh -s 4554 -i localhost:4551 &

peer_port=9998

xterm -e "./peer.py -s localhost:4554 -l $peer_port" &

sleep 1

firefox http://localhost:$peer_port
