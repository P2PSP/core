xterm -e './splitter_v1.py --channel /root/Audios/The_Last_of_the_Mohicans-promentory.ogg' &
echo "Splitter launched"

xterm -e './peer_v1.py --cluster_port 4553 --player_port 4554' &
echo "Monitor peer launched"

#sleep 1

#xterm -e 'netcat -d localhost 4554  > /dev/null' &
echo "Monitor listener launched"
echo "Please, consider to run the vlc in your host by meas of: vlc http://150.214.150.68:4554"

