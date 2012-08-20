
#!/bin/sh

#set -x

./run_source_134.sh -s 4552 -i "localhost:4551" &

peer_port=9999

./run_peer_134.sh -s "localhost:4552" -l $peer_port &

#set +x