xterm -e './splitter_v1.py' &
echo "Splitter launched"

xterm -e './peer_v1.py' &
echo "Trusted peer launched"

sleep 1

netcat localhost 9999 > /dev/null &
echo "Trusted listener launched"

sleep 5

xterm -e './peer_v1.py --listening_port=10000' &
echo "Normal peer launched"

vlc http://localhost:10000 &
echo "Normal listener launched"

