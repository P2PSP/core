#!/bin/sh

source=150.214.150.68:4554
peer_port=10000

usage() {
    echo $0
    echo "  [-s (source end-point, $source by default)]"
    echo "  [-l (listining peer port, $peer_port by defaults)]"
    echo "  [-? (help)]"
}

echo $0: parsing: $@

while getopts "s:l:?" opt; do
    case ${opt} in
	s)
	    source="${OPTARG}"
	    ;;
	l)
	    peer_port="${OPTARG}"
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

./peer.py -s $source -l $peer_port -b 128 &
#xterm -e "./peer.py -s $source -l $peer_port" &
#xterm -e "~/p2psp/peer.py -s localhost:4554 -l $peer_port" &

sleep 1

#firefox http://localhost:$peer_port &
vlc http://localhost:$peer_port > /dev/null 2> /dev/null &
