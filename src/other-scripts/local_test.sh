xterm -e './splitter_v1.py' &
echo "Splitter launched"

xterm -e './peer_v1.py --cluster_port=8889' &
echo "Monitor peer launched"

sleep 1

xterm -e 'netcat -d localhost 9999  > /dev/null' &
#netcat -d localhost 9999 > /dev/null &
echo "Monitor listener launched"

sleep 5

xterm -e './peer_v1.py --player_port=10000' &
echo "Normal peer launched"

vlc http://localhost:10000 &
echo "Normal listener launched"

