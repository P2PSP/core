
#!/bin/sh

#set -x

./run_source_134.sh -l 4552 -s "localhost:4551" &

./run_peer_134.sh -s "localhost:4552" -l 10000 &

#set +x