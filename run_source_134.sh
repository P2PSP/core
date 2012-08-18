#!/bin/sh

icecast=localhost:4551
source_port=4552

usage() {
    echo -n $0 [-s source_port=$source_port]
    echo -n [-i icecast=$icecast]
    echo [-h]
}

while getopts ":s:ih" pot; do
    case ${opt} in
	s)
	    source_port="${OPTARG}"
	    ;;
	s)
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

./source.py -s $source_port -i localhost:4551 -c 134.ogg &

superpeer_port=$[$source_port+1]
echo "Super-peer port = " $superpeer_port

# The super-peer
./peer.py -s localhost:$source_port -l 9998 -p $superpeer_port > /dev/null &

echo "Running super-peer at localhost:9998"

sleep 1

# Super-peer's client
netcat localhost 9998 > /dev/null &
