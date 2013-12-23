#!/bin/sh

#set -x

icecast=localhost:4551
source_port=4554

usage() {
    echo $0
    echo "  [-l (source port, $source_port by default)]"
    echo "  [-s (icecast end-point, $icecast by default)]"
    echo "  [-? (help)]"
}

echo $0: parsing: $@

while getopts "l:s:?" opt; do
    case ${opt} in
	l)
	    source_port="${OPTARG}"
	    ;;
	s)
	    icecast="${OPTARG}"
	    ;;
	?)
	    usage
	    exit 0
	    ;;
	\?)
	    echo "Invalid option: -${OPTARG}" >&2
	    usage
	    exit 1
	    ;;
	:)
	    echo "Option -${OPTARG} requires an argument." >&2
	    usage
	    exit 1
	    ;;
    esac
done

./source.py -l $source_port -s $icecast -c 480.ogg &

superpeer_port=$(($source_port+1))
echo "Running super-peer at localhost:"$superpeer_port

# The super-peer
./peer.py -s localhost:$source_port -l 9999 -p $superpeer_port > /dev/null &

sleep 1

# Super-peer's client
netcat localhost 9999 > /dev/null &

#set +x
