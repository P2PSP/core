xterm -r './run_oggfwd.sh' &
xterm -e '../splitter.py --source_hostname="localhost" --source_port=8000' &
xterm -e '../peer.py --source_hostname="localhost" --source_port=8000' &
vlc http://localhost:9999 &
