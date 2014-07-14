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

9. Decript a stream using the keyword "key":

    ./peer.py --keyword key &
    vlc http://localhost:9999 &

11. Join a private team using the password "pass":

    ./peer.py --password pass &
    vlc http://localhost:9999 &

12. Feed the local Icecast server, forever:

    xterm -e 'feed_icecast' &

13. Create a minimal local team (usually for testing purposes):

    # Feed the local Icecast server
    xterm -e 'splitter' &
    xterm -e 'peer' &
    vlc http://localhost:9999 &
    
# Splitter manual:

1. Create a channel using the default parameters:

   splitter &

2. Change the listening port to 5555:

   splitter --port 5555 &

3. Change the buffer size to 512 chunks:

   splitter --buffer_size 512 &

4. Change the source channel to "new_channel":

   splitter --channel new_channel &

5. Change the chunk size to 512 bytes:

   splitter --chunk_size 512 &

6. Change the source host to "new_host":

   splitter --source_addr new_host &

7. Change the source port to 6666:

   splitter --source_port 6666 &

8. Switch to IP multicast mode:

   splitter --mcast &

8. Select a particular IP multicast address 224.0.1.1:

   splitter --mcast --mcast_addr 224.0.1.1 &

9. Create a private team using the password "pass":

   splitter --password pass &

10. Encrypt the stream using the keyword "key":

   splitter --keyword key &

