#!/bin/bash

SoR=IMS

#export BUFFER_SIZE=512
#export CHANNEL="big_buck_bunny_720p_stereo.ogg"

#export BUFFER_SIZE=512
#export CHANNEL="big_buck_bunny_480p_stereo.ogg"

BUFFER_SIZE=512  # Important for the lost of chunks!!!
#export BUFFER_SIZE=128
#export BUFFER_SIZE=64
CHANNEL="BBB-134.ogv"

#export BUFFER_SIZE=32
#export CHANNEL="The_Last_of_the_Mohicans-promentory.ogg"

#export BUFFER_SIZE=128
#export CHANNEL="sintel_trailer-144p.ogg"

MAX_CHUNK_LOSS=8

HEADER_SIZE=10
MAX_CHUNK_DEBT=8
CHUNK_SIZE=1024
#export MAX_CHUNK_DEBT=32
#export MAX_CHUNK_DEBT=128
#export MAX_CHUNK_DEBT=32
#export MAX_CHUNK_DEBT=0
ITERATIONS=10
SOURCE_ADDR="127.0.0.1"
SOURCE_PORT=8080
SPLITTER_ADDR="127.0.0.1"
SPLITTER_PORT=4552
#export MCAST="--mcast"
MCAST_ADDR="224.0.0.1"
MCAST=""
#export MCAST_ADDR="0.0.0.0"
TEAM_PORT=5007
MAX_LIFE=180
BIRTHDAY_PERIOD=1
#export CHUNK_LOSS_PERIOD=100
CHUNK_LOSS_PERIOD=0

usage() {
    echo $0
    echo " Creates a local team."
    echo "  [-h header size in chunks ($HEADER_SIZE)]"
    echo "  [-b buffer size in chunks ($BUFFER_SIZE)]"
    echo "  [-c channel ($CHANNEL)]"
    echo "  [-k chunks size ($CHUNK_SIZE)]"
    echo "  [-d maximum chunk debt ($MAX_CHUNK_DEBT)]"
    echo "  [-l maximum chunk loss ($MAX_CHUNK_LOSS)]"
    echo "  [-i iterations of this script ($ITERATIONS)]"
    echo "  [-s source IP address, ($SOURCE_ADDR)]"
    echo "  [-o source port ($SOURCE_PORT)]"
    echo "  [-a splitter addr ($SPLITTER_ADDR)]"
    echo "  [-p splitter port ($SPLITTER_PORT)]"
    echo "  [-m /* Use IP multicast */ ($MCAST)]"
    echo "  [-r mcast addr ($MCAST_ADDR)]"
    echo "  [-t team port ($TEAM_PORT)]"
    echo "  [-f maximum life of a peer ($MAX_LIFE)]"
    echo "  [-y birthday period of a peer ($BIRTHDAY_PERIOD)]"
    echo "  [-w chunk loss period ($LOSS_PERIOD)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "h:b:c:k:d:l:i:s:o:a:p:mr:t:f:y:w:?" opt; do
    case ${opt} in
	h)
	    HEADER_SIZE="${OPTARG}"
	    echo "HEADER_SIZE="$HEADER_SIZE
	    ;;
	b)
	    BUFFER_SIZE="${OPTARG}"
	    echo "BUFFER_SIZE="$BUFFER_SIZE
	    ;;
	c)
	    CHANNEL="${OPTARG}"
	    echo "CHANNEL="$CHANNEL
	    ;;
	k)
	    CHUNK_SIZE="${OPTARG}"
	    echo "CHUNK_SIZE="$CHUNK_SIZE
	    ;;
	d)
	    MAX_CHUNK_DEBT="${OPTARG}"
	    echo "MAX_CHUNK_DEBT="$MAX_CHUNK_DEBT
	    ;;
	l)
	    MAX_CHUNK_LOSS="${OPTARG}"
	    echo "MAX_CHUNK_LOSS="$MAX_CHUNK_LOSS
	    ;;
	i)
	    ITERATIONS="${OPTARG}"
	    echo "ITERATIONS="$ITERATIONS
	    ;;
	s)
	    SOURCE_ADDR="${OPTARG}"
	    echo "SOURCE_ADDR="$SOURCE_ADDR
	    ;;
	o)
	    SOURCE_PORT="${OPTARG}"
	    echo "SOURCE_PORT="$SOURCE_PORT
	    ;;
	a)
	    SPLITTER_ADDR="${OPTARG}"
	    echo "SPLITTER_ADDR="$SPLITTER_ADDR
	    ;;
	p)
	    SPLITTER_PORT="${OPTARG}"
	    echo "SPLITTER_PORT="$SPLITTER_PORT
	    ;;
	m)
	    MCAST="--mcast"
	    echo "Using IP multicast"
	    ;;
	r)
	    MCAST_ADDR="${OPTARG}"
	    echo "MCAST_ADDR="$MCAST_ADDR
	    ;;
	t)
	    TEAM_PORT="${OPTARG}"
	    echo "TEAM_PORT="$TEAM_PORT
	    ;;
	f)
	    MAX_LIFE="${OPTARG}"
	    echo "MAX_LIFE="$MAX_LIFE
	    ;;
	y)
	    BIRTHDAY_PERIOD="${OPTARG}"
	    echo "BIRTHDAY_PERIOD="$BIRTHDAY_PERIOD
	    ;;
	w)
	    CHUNK_LOSS_PERIOD="${OPTARG}"
	    echo "CHUNK_LOSS_PERIOD="$CHUNK_LOSS_PERIOD
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

rm -f *.dat

SPLITTER="../splitter.py \
--buffer_size=$BUFFER_SIZE \
--channel=$CHANNEL \
--chunk_size=$CHUNK_SIZE \
--header_size=$HEADER_SIZE \
--max_chunk_loss=$MAX_CHUNK_LOSS \
$MCAST \
--mcast_addr=$MCAST_ADDR \
--port=$SPLITTER_PORT \
--source_addr=$SOURCE_ADDR \
--source_port=$SOURCE_PORT"

echo $SPLITTER

#xterm -sl 10000 -e $SPLITTER &
xterm -sl 10000 -e "$SPLITTER | tee splitter.dat" &

sleep 1

PEER="../src/peer.py \
--use_localhost \
--player_port=9999 \
--splitter_addr=$SPLITTER_ADDR \
--splitter_port=$SPLITTER_PORT"
# \
#--max_chunk_debt=$MAX_CHUNK_DEBT \
#--team_port=$TEAM_PORT"

echo $PEER

#xterm -sl 10000 -e $PEER &
xterm -T "Monitor" -sl 10000 -e "$PEER | tee monitor.dat" &

vlc http://localhost:9999 > /dev/null 2> /dev/null &

sleep 1

PEER="../peer.py \
--use_localhost \
--player_port=9998 \
--splitter_addr=$SPLITTER_ADDR \
--splitter_port=$SPLITTER_PORT"
# \
#--max_chunk_debt=$MAX_CHUNK_DEBT \
#--team_port=$TEAM_PORT"

echo $PEER

#xterm -sl 10000 -e $PEER &
xterm -sl 10000 -e "$PEER | tee peer.dat" &

vlc http://localhost:9998 > /dev/null 2> /dev/null &

x=1
while [ $x -le $ITERATIONS ]
do
    sleep $BIRTHDAY_PERIOD

    ./play.sh -a $SPLITTER_ADDR -p $SPLITTER_PORT -d $MAX_CHUNK_DEBT &

    x=$(( $x + 1 ))
done

sleep 1000

set +x
