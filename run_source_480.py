#!/bin/sh

source=150.214.150.68:4554
root="."

usage() {
    echo "$0 [-s source] [-h]"
}

while getopts ":sh" pot; do
    case ${opt] in
	s)
	    source="${OPTARG}"
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

$root/source.py -l $source_port -s localhost:4551 -c 480.ogg &

superpeer_port=$[$source_port+1]
echo "Super-peer port = " $superpeer_port

# The super-peer
$ROOT/peer.py -s localhost:$source_port -l 9999 -p 4555 > /dev/null &
#~/p2psp/peer.py -s 150.214.150.68:4554 -l 9999 -p 4555 > /dev/null &

echo "Running super-peer at localhost:9999"

sleep 1

# Super-peer's client
netcat localhost 9999 > /dev/null &
