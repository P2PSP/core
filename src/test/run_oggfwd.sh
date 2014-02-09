#!/bin/bash

icecast_name="localhost"
icecast_port=8000
video=~/Videos/Big_Buck_Bunny_small.ogv
#video=/home/jalvaro/workspace/sim/gnagl.ogg
#video=/home/jalvaro/workspaces-eclipse/P2PSP/Big_Buck_Bunny_small.ogv
#video=/home/jalvaro/workspaces-eclipse/P2PSP/sample48.ogg
password=hackme
channel=134.ogg

usage() {
    echo $0
    echo "  [-c (icecast mount-point, \"$channel\" by default)]"
    echo "  [-w (icecast password, \"$password\" by default)]"
    echo "  [-a (icecast hostname, $icecast_name by default)]"
    echo "  [-p (icecast port, $icecast_port by default)]"
    echo "  [-v (video file-name, \"$video\" by default)]"
    echo "  [-? (help)]"
}

echo $0: parsing: $@

while getopts "c:w:a:p:v:?" opt; do
    case ${opt} in
	c)
	    channel="${OPTARG}"
	    ;;
	w)
	    password="${OPTARG}"
	    ;;
	a)
	    icecast_name="${OPTARG}"
	    ;;
	p)
	    icecast_port="${OPTARG}"
	    ;;
	v)
	    video="${OPTARG}"
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

#old_IFS=$IFS
#IFS=":"
#icecast_host=${icecast[0]}
#icecast_port=${icecast[1]}
#IFS=$old_IFS

echo "Feeding http://$icecast_name:$icecast_port/$channel with \"$video\" forever ..."

set -x

while true
do
    oggfwd $icecast_name $icecast_port $password $channel < $video
done

set +x
