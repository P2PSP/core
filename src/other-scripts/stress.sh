#!/bin/sh

export SPLITTER_PORT=4552
export MONITOR_PORT=4553

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

xterm -e './splitter.py --addr localhost --port $SPLITTER_PORT' &

sleep 1
xterm -e './peer.py --splitter_host localhost --splitter_port $SPLITTER_PORT --team_port $MONITOR_PORT --player_port 9998' &
vlc http://localhost:9998 &

x=1
while [ $x -le 20 ]
do
    echo $i
    sleep 1
    TIME=`shuf -i 1-10 -n 1`
    echo $TIME
    export PORT=`shuf -i 2000-65000 -n 1`
    timelimit -t $TIME xterm -e './peer.py --splitter_host localhost --splitter_port $SPLITTER_PORT --player_port $PORT' &
    TIME=`shuf -i 1-10 -n 1`
    echo $TIME
    timelimit -t $TIME vlc http://localhost:$PORT &
    x=$(( $x + 1 ))
done
