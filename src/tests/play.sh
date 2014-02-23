#!/bin/sh

export DEBT_MEMORY=1024
export DEBT_THRESHOLD=1024
export SPLITTER_ADDR="150.214.150.68"
export SPLITTER_PORT=4552

usage() {
    echo $0
    echo "  [-m debt memory ($DEB_MEMORY)]"
    echo "  [-d debt threshold ($DEB_THRESHOLD)]"
    echo "  [-s splitter IP address ($SPLITTER_ADDR)]"
    echo "  [-l splitter port ($SPLITTER_PORT)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "d:m:s:l:?" opt; do
    case ${opt} in
	m)
	    DEBT_MEMORY="${OPTARG}"
	    ;;
	d)
	    DEBT_THRESHOLD="${OPTARG}"
	    ;;
	s)
	    SPLITTER_ADDR="${OPTARG}"
	    ;;
	l)
	    SPLITTER_PORT="${OPTARG}"
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

export PLAYER_PORT=`shuf -i 2000-65000 -n 1`
xterm -e '../peer.py --port 4552 --player_port $PLAYER_PORT --splitter_addr $SPLITTER_ADDR --splitter_port $SPLITTER_PORT --debt_threshold $DEBT_THRESHOLD --debt_memory $DEBT_MEMORY' &
vlc http://localhost:$PLAYER_PORT &
