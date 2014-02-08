export SPLITTER_PORT=4552
export MONITOR_PORT=4553

xterm -e './splitter.py --addr localhost --port $SPLITTER_PORT' &
#xterm -e './splitter_v1.py --cluster_host localhost --cluster_port $TEAM_PORT' &
echo "Splitter launched"

xterm -e './peer.py --splitter_host localhost --splitter_port $SPLITTER_PORT --team_port $MONITOR_PORT --player_port 9998' &
echo "Monitor peer launched"

sleep 1

vlc http://localhost:9998 &
#xterm -e 'netcat -d localhost 9998  > /dev/null' &
#netcat -d localhost 9998 > /dev/null &
echo "Monitor listener launched"

sleep 5

xterm -e './peer.py --splitter_host localhost --splitter_port $SPLITTER_PORT --player_port 9999' &
echo "Normal peer launched"

vlc http://localhost:9999 &
echo "Normal listener launched"

