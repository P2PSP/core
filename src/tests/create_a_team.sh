#!/bin/sh

#export BUFFER_SIZE=256
#export CHANNEL="/root/Videos/Big_Buck_Bunny_small.ogv"
#export BUFFER_SIZE=128
#export CHANNEL="/root/Audios/The_Last_of_the_Mohicans-Promentory.ogg"
export BUFFER_SIZE=128
export CHANNEL="/root/Videos/sintel_trailer-144p.ogg"
export CHUNK_SIZE=1024
export DEBT_MEMORY=1024
export DEBT_THRESHOLD=32
export ITERATIONS=100
export LOSSES_MEMORY=1024
export LOSSES_THRESHOLD=128
export SOURCE_ADDR="150.214.150.68"
export SOURCE_PORT=4551
export SPLITTER_PORT=5555
export LIFE=60
export BIRTHDAY=30

usage() {
    echo $0
    echo "  [-b buffer size ($BUFFER_SIZE)]"
    echo "  [-c channel ($CHANNEL)]"
    echo "  [-u chunks size ($CHUNK_SIZE)]"
    echo "  [-m debt memory ($DEB_MEMORY)]"
    echo "  [-d debt threshold ($DEB_THRESHOLD)]"
    echo "  [-i iterations ($ITERATIONS)]"
    echo "  [-e losses memory ($LOSSES_MEMORY)]"
    echo "  [-l losses threshold ($LOSSES_THRESHOLD)]"
    echo "  [-s source IP address, ($SOURCE_ADDR)]"
    echo "  [-o source port ($SOURCE_PORT)]"
    echo "  [-p splitter port ($SPLITTER_PORT)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "b:c:u:m:d:i:e:l:s:o:p:?" opt; do
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
	m)
	    DEBT_MEMORY="${OPTARG}"
	    ;;
	d)
	    DEBT_THRESHOLD="${OPTARG}"
	    ;;
	i)
	    ITERATIONS="${OPTARG}"
	    ;;
	e)
	    LOSSES_MEMORY="${OPTARG}"
	    ;;
	l)
	    LOSSES_THRESHOLD="${OPTARG}"
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

xterm -e '../splitter.py  --addr localhost --buffer_size=$BUFFER_SIZE --channel $CHANNEL --chunk_size=$CHUNK_SIZE --losses_threshold=$LOSSES_THRESHOLD --losses_memory=$LOSSES_MEMORY --port $SPLITTER_PORT --source_addr $SOURCE_ADDR --source_port $SOURCE_PORT' &

sleep 1

xterm -e '../peer.py --debt_threshold=$DEBT_THRESHOLD --debt_memory=$DEBT_MEMORY --player_port 9998 --splitter_addr localhost --splitter_port $SPLITTER_PORT' &
vlc http://localhost:9998 &

x=1
while [ $x -le $ITERATIONS ]
do
    sleep $BIRTHDAY
    export PORT=`shuf -i 2000-65000 -n 1`

    xterm -e '../peer.py --debt_threshold=$DEBT_THRESHOLD --debt_memory=$DEBT_MEMORY --player_port $PORT --splitter_addr localhost --splitter_port $SPLITTER_PORT' &

    TIME=`shuf -i 1-$LIFE -n 1`
    timelimit -t $TIME vlc http://localhost:$PORT &
    x=$(( $x + 1 ))
done
