#!/bin/sh

source=150.214.150.68:4554
peer_port=9999

usage() {
    echo -n $0 [-s source=$source]
    echo -n [-l peer_port=$peer_port]
    echo [-h]
}

while getopts ":s:ph" pot; do
    case ${opt} in
	s)
	    source="${OPTARG}"
	    ;;
	l)
	    peer_port="${OPTARG}"
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

./peer.py -s $source -l $peer_port &
#xterm -e "~/p2psp/peer.py -s $source -l $peer_port" &
#xterm -e "~/p2psp/peer.py -s localhost:4554 -l $peer_port" &

sleep 1

#firefox http://localhost:$peer_port &
vlc http://localhost:$peer_port > /dev/null 2> /dev/null &
