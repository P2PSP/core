#!/bin/bash

export CHANNEL=""
export SOURCE_PORT=8080
export VIDEO="$HOME/Videos/Big_Buck_Bunny_small.ogv"

usage() {
    echo $0
    echo " Run a source."
    echo "  [-c channel ($CHANNEL)]"
    echo "  [-o source port ($SOURCE_PORT)]"
    echo "  [-v video ($VIDEO)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "c:o:v:?" opt; do
    case ${opt} in
	c)
	    CHANNEL="${OPTARG}"
	    echo "CHANNEL="$CHANNEL
	    ;;
	o)
	    SOURCE_PORT="${OPTARG}"
	    echo "LOSSES_THRESHOLD="$SOURCE_PORT
	    ;;
	v)
	    VIDEO="${OPTARG}"
	    echo "VIDEO="$VIDEO
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

vlc $VIDEO --sout "#duplicate{dst=standard{mux=ogg,dst=:$SOURCE_PORT/$CHANNEL,access=http}}" &
