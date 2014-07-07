P2PSP manual
============

# Peer manual:

How to:

1. Watch the default channel:

    ./peer.py &
    vlc http://localhost:9999

or simply:

    ./play.sh &

2. Change the local port (9998) to communicate with VLC:

    ./peer.py --player_port 9998 &
    vlc http://localhost:9998 &

3. Watch a particular channel (4554):

    ./peer.py --splitter_port 4554 &
    vlc http://localhost:9999 &

4. Use a specific team port (8888) for communicating with the rest of
   the team (you should use this feature in order, for example, to create
   a NAT entry manualy):

    ./peer.py --team_port 8888 &
    vlc http://localhost:9999 &

5. Use a particular splitter host (1.2.3.4):

    ./peer.py --splitter_addr 1.2.3.4 &
    vlc http://localhost:9999 &

6. Run a monitor peer (the monitor peer is the first peer of the team
   that contacts the splitter):

    ./peer.py --monitor &
    vlc http://localhost:9999 &

9. Decript a stream using the key "key":

    ./peer.py --key key &
    vlc http://localhost:9999 &

11. Join a private team using the password "password":

    ./peer.py --pass password &
    vlc http://localhost:9999 &

12. Feed the local Icecast server, forever:

    xterm -e 'feed_icecast' &

13. Create a minimal local team (usually for testing purposes):

    # Feed the local Icecast server
    xterm -e 'splitter' &
    xterm -e 'peer' &
    vlc http://localhost:9999 &
    
# Splitter manual:

* Create a channel (unfinished):

./splitter &
