P2PSP manual
============

How to:

1. Watch the default channel:

./peer.py &
vlc http://localhost:9999

or simply:

./play.sh

2. Change the local port (9998) to communicate with VLC:

./peer.py --player_port 9998 &
vlc http://localhost:9998

3. Watch a particular channel (4554):

./peer.py --splitter_port 4554 &
vlc http://localhost:9999

4. Use a specific team port (8888) for communicating with the rest of
   peers (you should use this feature in order, for example, to create
   a NAT entry manualy or to select the channel in the IP multicast
   mode (in this case, all channels are transmitted throught the
   224.0.0.1 multicast address, by default)):

./peer.py --team_port 8888 &
vlc http://localhost:9999

5. Use a particular splitter host (1.2.3.4):

./peer.py --splitter_addr 1.2.3.4 &
vlc http://localhost:9999

6. Run a monitor peer (notice that this must be the first peer of
   the team that contacts the splitter):

./peer.py --monitor &
vlc http://localhost:9999

7. Run a peer in IP multicast mode (the default IP multicast address
   is 224.0.0.1 and the port is 8888):

./peer.py --mcast &
vlc http://localhost:9999

8. Define a new IP multicast channel (224.1.1.1:7777):

./peer.py --mcast --team_addr 224.1.1.1 --team_port 7777 &
vlc http://localhost:9999

9. Enable the CPS (Content Privacy Set of rules) in the IP multicast mode:

./peer.py --mcast --cps key &
vlc http://localhost:9999

10. Join a private team using the password "password":

./peer.py --pass password &
vlc http://localhost:9999

11. Enable the CPS in the IP unicast mode:

./register --addr my_public_IP_address --port my_public_port --pass password
./peer.py --cps password &
vlc http://localhost:9999

* Create a channel (unfinished):

./splitter &
