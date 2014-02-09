#!/bin/sh

export BUFFER_SIZE=256
export CHANNEL="/root/Videos/Big_Buck_Bunny_small.ogv"
export CHUNK_SIZE=1024
export CROWD=10
export DEBT_THRESHOLD=32
export LOSSES_THRESHOLD=1
export MONITOR_PORT=4553
export SOURCE_ADDR="150.214.150.68"
export SOURCE_PORT=4551
export SPLITTER_PORT=4552
export TIME=60

usage() {
    echo $0
    echo "  [-b buffer size ($BUFFER_SIZE)]"
    echo "  [-c channel ($CHANNEL)]"
    echo "  [-u chunks size ($CHUNK_SIZE)]"
    echo "  [-w crowd ($CROWD)]"
    echo "  [-d debt threshold ($DEB_THRESHOLD)]"
    echo "  [-l losses threshold ($LOSSES_THRESHOLD)]"
    echo "  [-m monitor IP address ($MONITOR_PORT)]"
    echo "  [-s source IP address, ($SOURCE_ADDR)]"
    echo "  [-o source port ($SOURCE_PORT)]"
    echo "  [-p splitter port ($SPLITTER_PORT)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "b:c:u:w:d:l:m:s:o:p:t:?" opt; do
    case ${opt} in
	b)
	    BUFFER_SIZE="${OPTARG}"
	    ;;
	c)
	    CHANNEL="${OPTARG}"
	    ;;
	u)
	    CHUNK_SIZE="${OPTARG}"
	    ;;
	w)
	    CROWD="${OPTARG}"
	    ;;
	d)
	    DEBT_THRESHOLD="${OPTARG}"
	    ;;
	l)
	    LOSSES_THRESHOLD="${OPTARG}"
	    ;;
	m)
	    MONITOR_PORT="${OPTARG}"
	    ;;
	s)
	    SOURCE_ADDR="${OPTARG}"
	    ;;
	o)
	    SOURCE_PORT="${OPTARG}"
	    ;;
	p)
	    SPLITTER_PORT="${OPTARG}"
	    ;;
	t)
	    TIME="${OPTARG}"
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

set -x
xterm -e './splitter.py  --addr localhost --buffer_size=$BUFFER_SIZE --channel $CHANNEL --chunk_size=$CHUNK_SIZE --losses_threshold=$LOSSES_THRESHOLD --port $SPLITTER_PORT --source_addr $SOURCE_ADDR --source_port $SOURCE_PORT' &
sleep 1
xterm -e './peer.py --debt_threshold=$DEBT_THRESHOLD --player_port 9998 --port $MONITOR_PORT --splitter_addr localhost --splitter_port $SPLITTER_PORT' &
vlc http://localhost:9998 &

x=1
while [ $x -le $CROWD ]
do
    sleep 1
    export PORT=`shuf -i 2000-65000 -n 1`
    xterm -e './peer.py --debt_threshold=$DEBT_THRESHOLD  --player_port $PORT --splitter_addr localhost --splitter_port $SPLITTER_PORT' &
    timelimit -t $TIME vlc http://localhost:$PORT &
    x=$(( $x + 1 ))
done
