#!/bin/sh

SoR=IMS

#export BUFFER_SIZE=512
#export CHANNEL="big_buck_bunny_720p_stereo.ogg"

#export BUFFER_SIZE=512
#export CHANNEL="big_buck_bunny_480p_stereo.ogg"

export BUFFER_SIZE=64
export CHANNEL="/Big_Buck_Bunny_small.ogv"

#export BUFFER_SIZE=32
#export CHANNEL="The_Last_of_the_Mohicans-Promentory.ogg"

#export BUFFER_SIZE=128
#export CHANNEL="sintel_trailer-144p.ogg"

export LOSSES_MEMORY=32
export LOSSES_THRESHOLD=8
export CHUNK_SIZE=1024
export DEBT_MEMORY=1024
export DEBT_THRESHOLD=32
export ITERATIONS=100

export SOURCE_ADDR="localhost"
export SOURCE_PORT=8000
export SPLITTER_ADDR="localhost"
export SPLITTER_PORT=4552
#export TEAM_ADDR="224.1.1.1"
export TEAM_PORT=5007
export LIFE=180
export BIRTHDAY=10
export LOSS_PERIOD=100

usage() {
    echo $0
    echo " Creates a local team."
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
    echo "  [-a splitter addr ($SPLITTER_ADDR)]"
    echo "  [-p splitter port ($SPLITTER_PORT)]"
#    echo "  [-t team addr ($TEAM_ADDR)]"
    echo "  [-r team port ($SPLITTER_PORT)]"
    echo "  [-f life ($LIFE)]"
    echo "  [-y birthday ($BIRTHDAY)]"
    echo "  [-w loss period ($LOSS_PERIOD)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "b:c:u:m:d:i:e:l:s:o:p:r:f:y:w:?" opt; do
    case ${opt} in
	b)
	    BUFFER_SIZE="${OPTARG}"
	    echo "BUFFER_SIZE="$BUFFER_SIZE
	    ;;
	c)
	    CHANNEL="${OPTARG}"
	    echo "CHANNEL="$CHANNEL
	    ;;
	u)
	    CHUNK_SIZE="${OPTARG}"
	    echo "CHUNK_SIZE="$CHUNK_SIZE
	    ;;
	m)
	    DEBT_MEMORY="${OPTARG}"
	    echo "DEBT_MEMORY="$DEBT_MEMORY
	    ;;
	d)
	    DEBT_THRESHOLD="${OPTARG}"
	    echo "DEBT_THRESHOLD="$DEBT_THRESHOLD
	    ;;
	i)
	    ITERATIONS="${OPTARG}"
	    echo "ITERATIONS="$DEBT_THRESHOLD=
	    ;;
	e)
	    LOSSES_MEMORY="${OPTARG}"
	    echo "LOSSES_MEMORY="$LOSSES_MEMORY
	    ;;
	l)
	    LOSSES_THRESHOLD="${OPTARG}"
	    echo "LOSSES_THRESHOLD="$LOSSES_THRESHOLD
	    ;;
	s)
	    SOURCE_ADDR="${OPTARG}"
	    echo "LOSSES_THRESHOLD="$SOURCE_ADDR
	    ;;
	o)
	    SOURCE_PORT="${OPTARG}"
	    echo "LOSSES_THRESHOLD="$SOURCE_ADDR
	    ;;
	a)
	    SPLITTER_ADDR="${OPTARG}"
	    echo "SPLITTER_ADDR="$SPLITTER_ADDR
	    ;;
	p)
	    SPLITTER_PORT="${OPTARG}"
	    echo "SPLITTER_PORT="$SPLITTER_PORT
	    ;;
#	t)
#	    TEAM_ADDR="${OPTARG}"
#	    echo "TEAM_ADDR="$TEAM_ADDR
#	    ;;
	r)
	    TEAM_PORT="${OPTARG}"
	    echo "TEAM_PORT="$TEAM_PORT
	    ;;
	f)
	    LIFE="${OPTARG}"
	    echo "LIFE="$LIFE
	    ;;
	y)
	    BIRTHDAY="${OPTARG}"
	    echo "BIRTHDAY="$BIRTHDAY
	    ;;
	w)
	    LOSS_PERIOD="${OPTARG}"
	    echo "LOSS_PERIOD="$LOSS_PERIOD
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

xterm -sl 10000 -e './splitter_IMS.py --splitter_addr $SPLITTER_ADDR --splitter_port $SPLITTER_PORT --team_addr $TEAM_ADDR --team_port $TEAM_PORT --buffer_size=$BUFFER_SIZE --channel $CHANNEL --chunk_size=$CHUNK_SIZE --losses_threshold=$LOSSES_THRESHOLD --losses_memory=$LOSSES_MEMORY --source_addr $SOURCE_ADDR --source_port $SOURCE_PORT' &
#xterm -sl 10000 -e '../splitter.py  --team_addr localhost --buffer_size=$BUFFER_SIZE --channel $CHANNEL --chunk_size=$CHUNK_SIZE --losses_threshold=$LOSSES_THRESHOLD --losses_memory=$LOSSES_MEMORY --team_port $SPLITTER_PORT --source_addr $SOURCE_ADDR --source_port $SOURCE_PORT > splitter' &

sleep 1

xterm -sl 10000 -e '../peer_IMS.py --debt_threshold=$DEBT_THRESHOLD --debt_memory=$DEBT_MEMORY --player_port 9998 --splitter_addr $SPLITTER_ADDR --splitter_port $SPLITTER_PORT --team_port $TEAM_PORT --monitor' &
#xterm -sl 10000 -e '../peer.py --debt_threshold=$DEBT_THRESHOLD --debt_memory=$DEBT_MEMORY --player_port 9998 --splitter_addr localhost --splitter_port $SPLITTER_PORT --monitor > monitor' &

vlc http://localhost:9998 &
exit

x=1
while [ $x -le $ITERATIONS ]
do
    sleep $BIRTHDAY
    export PLAYER_PORT=`shuf -i 2000-65000 -n 1`
    #export TEAM_PORT=`shuf -i 2000-65000 -n 1`

    #sudo iptables -A POSTROUTING -t mangle -o lo -p udp -m multiport --sports $TEAM_PORT -j MARK --set-xmark 101
    #sudo iptables -A POSTROUTING -t mangle -o lo -p udp -m multiport --sports $TEAM_PORT -j RETURN

    xterm -sl 10000 -e '../peer_$SoR.py --debt_threshold=$DEBT_THRESHOLD --debt_memory=$DEBT_MEMORY --player_port $PLAYER_PORT --splitter_addr localhost --splitter_port $SPLITTER_PORT --chunk_loss_period $LOSS_PERIOD' &

    #xterm -sl 10000 -e '../peer.py --team_port $TEAM_PORT --debt_threshold=$DEBT_THRESHOLD --debt_memory=$DEBT_MEMORY --player_port $PLAYER_PORT --splitter_addr localhost --splitter_port $SPLITTER_PORT' &

    TIME=`shuf -i 1-$LIFE -n 1`
    timelimit -t $TIME vlc http://localhost:$PLAYER_PORT &
    x=$(( $x + 1 ))
done

set +x
