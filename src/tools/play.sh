#!/bin/sh

export MAX_CHUNK_DEBT=32
export SPLITTER_ADDR="150.214.150.68"
export SPLITTER_PORT=4552
export TEAM_PORT=5555

usage() {
    echo $0
    echo "Play a channel"
    echo "  [-d maximum chunk debt ($MAX_CHUNK_DEBT)]"
    echo "  [-a splitter IP address ($SPLITTER_ADDR)]"
    echo "  [-p splitter port ($SPLITTER_PORT)]"
    echo "  [-t team port ($SPLITTER_PORT)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "d:a:p:t:?" opt; do
    case ${opt} in
	d)
	    MAX_CHUNK_DEBT="${OPTARG}"
	    echo "MAX_CHUNK_DEBT="$MAX_CHUNK_DEBT
	    ;;
	a)
	    SPLITTER_ADDR="${OPTARG}"
	    ;;
	p)
	    SPLITTER_PORT="${OPTARG}"
	    ;;
	t)
	    TEAM_PORT="${OPTARG}"
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

PEER="python3 -O ../peer.py \
--player_port $PLAYER_PORT \
--splitter_addr $SPLITTER_ADDR \
--splitter_port $SPLITTER_PORT"
# \
#--team_port $TEAM_PORT"

echo $PEER

xterm -sl 10000 -e "$PEER | tee $PLAYER_PORT.dat" &

# sleep 1; netcat localhost $PLAYER_PORT -v > /dev/null &

sleep 1; vlc http://localhost:$PLAYER_PORT &

