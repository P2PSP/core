#!/bin/sh

export BUFFER_SIZE=256
export CHANNEL="/root/Videos/Big_Buck_Bunny_small.ogv"
#export CHANNEL="/root/Audios/The_Last_of_the_Mohicans-Promentory.ogg"
export CHUNK_SIZE=1024
export DEBT_THRESHOLD=32
export LOSSES_THRESHOLD=128
export MONITOR_PORT=0
export PLAYER_PORT=9999
export SOURCE_ADDR="150.214.150.68"
export SOURCE_PORT=4551
export SPLITTER_ADDR="localhost"
export SPLITTER_PORT=5555

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

#xterm -e '../splitter.py  --addr localhost --buffer_size=$BUFFER_SIZE --channel $CHANNEL --chunk_size=$CHUNK_SIZE --losses_threshold=$LOSSES_THRESHOLD --port $SPLITTER_PORT --source_addr $SOURCE_ADDR --source_port $SOURCE_PORT > splitter' &
xterm -e '../splitter.py  --addr localhost --buffer_size=$BUFFER_SIZE --channel $CHANNEL --chunk_size=$CHUNK_SIZE --losses_threshold=$LOSSES_THRESHOLD --port $SPLITTER_PORT --source_addr $SOURCE_ADDR --source_port $SOURCE_PORT' &

read

sleep 1
#xterm -e '../peer.py --debt_threshold=$DEBT_THRESHOLD --player_port 9998 --port $MONITOR_PORT --splitter_addr localhost --splitter_port $SPLITTER_PORT > monitor' &
xterm -e '../peer.py --debt_threshold=$DEBT_THRESHOLD --player_port 9998 --port $MONITOR_PORT --splitter_addr localhost --splitter_port $SPLITTER_PORT' &
vlc http://localhost:9998 &

sleep 10
#xterm -e '../peer.py --debt_threshold=$DEBT_THRESHOLD  --player_port $PLAYER_PORT --splitter_addr $SPLITTER_ADDR --splitter_port $SPLITTER_PORT > peer' &
xterm -e '../peer.py --debt_threshold=$DEBT_THRESHOLD  --player_port $PLAYER_PORT --splitter_addr $SPLITTER_ADDR --splitter_port $SPLITTER_PORT' &
vlc http://localhost:$PLAYER_PORT &
