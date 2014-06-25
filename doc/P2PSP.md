P2PSP manual
============

(Please, see the examples of the "test" directory to extend this information.)

I want to:

* See the default channel:

./peer.py &
vlc http://localhost:9999

* Use a particular local port (9998) to communicate with VLC:

./peer.py --player_port 9998 &
vlc http://localhost:9998

* See a particular channel (4554):

./peer.py --splitter_port 4554 &
vlc http://localhost:9999

* Use a particular team port (8888) for communicating with the rest
  of peers:

./peer.py --team_port 8888 &
vlc http://localhost:9999

* Use a particular splitter host (1.2.3.4):

./peer.py --splitter_addr 1.2.3.4 &
vlc http://localhost:9999

* Run a monitor peer (notice that this should be the first peer in the
  team):

./peer.py --monitor &
vlc http://localhost:9999

* Create a channel (unfinished):

./splitter &
