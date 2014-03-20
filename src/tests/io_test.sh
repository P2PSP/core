#!/bin/bash

export BUFFER_SIZE=512
export CHANNEL="/root/Videos/big_buck_bunny_720p_stereo.ogg"

export BUFFER_SIZE=512
export CHANNEL="/root/Videos/big_buck_bunny_480p_stereo.ogg"

#export BUFFER_SIZE=512
#export CHANNEL="/root/Videos/Big_Buck_Bunny_small.ogv "

export SOURCE_ADDR="150.214.150.68"
export SOURCE_PORT=4551
export SPLITTER_PORT=4558

usage() {
    echo $0
    echo "  [-b buffer size ($BUFFER_SIZE)]"
    echo "  [-c channel ($CHANNEL)]"
    echo "  [-s source IP address, ($SOURCE_ADDR)]"
    echo "  [-o source port ($SOURCE_PORT)]"
    echo "  [-p splitter port ($SPLITTER_PORT)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "b:c:s:o:p:?" opt; do
    case ${opt} in
	b)
	    BUFFER_SIZE="${OPTARG}"
	    ;;
	c)
	    CHANNEL="${OPTARG}"
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


xterm -e '../splitter.py --buffer_size=$BUFFER_SIZE --channel $CHANNEL --port $SPLITTER_PORT --losses_threshold 256' &

sleep 1

export monitor_port=$[$SPLITTER_PORT+1]
xterm -e '../peer.py --port $monitor_port --player_port 19999 --splitter_port $SPLITTER_PORT --debt_threshold 10000 > /dev/null' &

sleep 1

xterm -e '/bin/netcat localhost 19999 > /dev/null' &

