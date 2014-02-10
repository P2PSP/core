#!/bin/sh

export DEBT_THRESHOLD=32
export PLAYER_PORT=9999
export SPLITTER_ADDR="150.214.150.68"
export SPLITTER_PORT=4552

usage() {
    echo $0
    echo "  [-d debt threshold ($DEB_THRESHOLD)]"
    echo "  [-p player port ($PLAYER_PORT)]"
    echo "  [-s splitter IP address ($SPLITTER_ADDR)]"
    echo "  [-l splitter port ($SPLITTER_PORT)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "d:p:s:l:?" opt; do
    case ${opt} in
	d)
	    DEBT_THRESHOLD="${OPTARG}"
	    ;;
	p)
	    PLAYER_PORT="${OPTARG}"
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

echo
echo "Please, close the VLC to leave the team (don't kill the peer)!"
echo
echo "Hit <enter> to continue ..." 
read

xterm -e './peer.py --debt_threshold=$DEBT_THRESHOLD  --player_port $PLAYER_PORT --splitter_addr $SPLITTER_ADDR --splitter_port $SPLITTER_PORT' &
vlc http://localhost:$PLAYER_PORT &
