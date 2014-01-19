xterm -e './splitter_v1.py --cluster_host localhost --cluster_port 4552' &
echo "Splitter launched"

xterm -e './peer_v1.py --splitter_host localhost --splitter_port 4552 --cluster_port 4553 --player_port 9998' &
echo "Monitor peer launched"

sleep 1

xterm -e 'netcat -d localhost 9998  > /dev/null' &
#netcat -d localhost 9998 > /dev/null &
echo "Monitor listener launched"

sleep 5

xterm -e './peer_v1.py --splitter_host localhost --splitter_port 4552 --player_port 9999' &
echo "Normal peer launched"

vlc http://localhost:9999 &
echo "Normal listener launched"

