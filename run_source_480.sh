#!/bin/sh

#set -x

icecast=localhost:4551
source_port=4554

usage() {
    echo $0
    echo "  [-s (source port, $source_port by default)]"
    echo "  [-i (icecast end-point, $icecast by default)]"
    echo "  [-h (help)]"
}

echo $0: parsing: $@

while getopts "s:i:h" opt; do
    case ${opt} in
	s)
	    source_port="${OPTARG}"
	    ;;
	i)
	    icecast="${OPTARG}"
	    ;;
	h)
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

./source.py -s $source_port -i $icecast -c 480.ogg &

superpeer_port=$(($source_port+1))
echo "Running super-peer at localhost:"$superpeer_port

# The super-peer
./peer.py -s localhost:$source_port -l 9998 -p $superpeer_port > /dev/null &
#~/p2psp/peer.py -s 150.214.150.68:4554 -l 9999 -p 4555 > /dev/null &

sleep 1

# Super-peer's client
netcat localhost 9998 > /dev/null &

#set +x