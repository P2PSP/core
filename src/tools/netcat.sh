#!/bin/bash

PORT=$1

#x=0
#while true;
#do
#    echo $x
#    x=$(( $x + 1 ))
echo $0 $@
netcat localhost $PORT > /dev/null
#done

