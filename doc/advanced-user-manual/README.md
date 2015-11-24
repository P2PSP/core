P2PSP "advanced" manual
=======================

Please, first head over [User Manual](../user-manual/README.md).

# Peer:

<!-- {{{  -->

1. Watch the default channel:
<!-- {{{  -->
    ```
    ./peer.py &
    vlc http://localhost:9999
    ```
<!-- }}} -->

2. Change the local port (9998) to communicate with VLC:
<!-- {{{  -->
	```
	./peer.py --player_port=9998 &
	vlc http://localhost:9998 &
	```
<!-- }}} -->

3. Watch a particular channel (in the port 4554):
<!-- {{{  -->
    ```
    ./peer.py --splitter_port=4554 &
    vlc http://localhost:9999 &
    ```
<!-- }}} -->
    
4. Use a specific team port (8888) for communicating with the rest of
   the team (you should use this feature, for example, after having
   created a NAT entry manualy):
<!-- {{{  -->
    ```
    ./peer.py --team_port=8888 &
    vlc http://localhost:9999 &
    ```
<!-- }}} -->

5. Use a particular splitter host (1.2.3.4):
<!-- {{{  -->
    ```
    ./peer.py --splitter_host=1.2.3.4 &
    vlc http://localhost:9999 &
    ```
<!-- }}} -->

6. Decript a stream using the keyword "key" (not yet implemented):
<!-- {{{  -->
    ```
    ./peer.py --keyword=key &
    vlc http://localhost:9999 &
    ```
<!-- }}} -->

7. Join a private team using the password "pass" (not yet implemented):
<!-- {{{  -->
    ```
    ./peer.py --password=pass &
    vlc http://localhost:9999 &
    ```
<!-- }}} -->

8. Deliberately loss a chunk of each 100 (usually for testing purposes):
<!-- {{{  -->
    ```
    ./peer.py --chunk_loss_period=100
    ```
<!-- }}} -->

<!-- }}} -->

# Splitter:
<!-- {{{  -->

1. Create a channel using the default parameters (run "splitter --help"):
<!-- {{{  -->
    ```
    splitter &
    ```
<!-- }}} -->

2. Change the listening port to 5555:
<!-- {{{  -->
    ```
    splitter --port=5555 &
    ```
<!-- }}} -->

3. Change the buffer size to 512 chunks:
<!-- {{{  -->
    ```
    splitter --buffer_size=512 &
    ```
<!-- }}} -->

4. Change the source channel (media stream) to "new_channel":
<!-- {{{  -->
    ```
    splitter --channel=new_channel &
    ```
<!-- }}} -->

5. Change the chunk size to 512 bytes:
<!-- {{{  -->
    ```
    splitter --chunk_size=512 &
    ```
<!-- }}} -->

6. Change the source host (which runs Icecast for example) to
   "new_host":
<!-- {{{  -->
    ```
    splitter --source_host=new_host &
    ```
<!-- }}} -->

7. Change the source port (where Icecast is listening) to 6666:
<!-- {{{  -->
    ```
    splitter --source_port=6666 &
    ```
<!-- }}} -->

8. Create a private team using the password "pass" (not yet implemented):
<!-- {{{  -->
    ```
    splitter --password=pass &
    ```
<!-- }}} -->

9. Encrypt the stream using the keyword "key" (not yet implemented):
<!-- {{{  -->
    ```
    splitter --keyword=key &
    ```
<!-- }}} -->

10. Use the IP multicast mode (if available):
<!-- {{{  -->
    ```
    splitter --mcast &
    ```
<!-- }}} -->

11. Select a particular IP multicast address 224.0.1.1:
<!-- {{{  -->
    ```
    splitter --mcast --mcast_addr=224.0.1.1 &
    ```
<!-- }}} -->

<!-- }}} -->

# Miscellaneous:
<!-- {{{  -->

* Download
[Big_Buck_Bunny_small.ogv](http://commons.wikimedia.org/wiki/File:Big_Buck_Bunny_small.ogv).

* Feed a local Icecast server, forever (until kill the process):
<!-- {{{  -->

    ```
    xterm -e './tools/feed_icecast.sh' &
    ```

<!-- }}} -->

* Use VLC as source (support several HTTP clients).
<!-- {{{  -->

   Media -> Broadcast -> Select the archive -> Broadcast -> Next -> HTTP ->
   Show in local + Add + Path=/x.ogv -> [Not] transcode -> Next -> Stream

<!-- }}} -->

* Create (manually) a local team (usually for testing purposes):
<!-- {{{  -->

    ```
    # Remember first to feed the source server!!!
                                                             
    xterm -e './src/splitter.py' &                # Run a splitter
    xterm -e './src/peer.py' &                    # Run a (monitor) peer
    xterm -e './src/peer.py --player_port=9998' & # Run a peer
    vlc http://localhost:9999 &                   # Run a player for the monitor
    vlc http://localhost:9998 &                   # Run a player for the peer
    ```

<!-- }}} -->

* Create (automatically) a local team:
<!-- {{{  -->

    ```
    # Remember first to feed the source server!!!
    ./tools/create_a_team.sh # Create the team
    ```

<!-- }}} -->

* To run in debug mode:
<!-- {{{  -->

    ```
    python -d example.py
    ```

<!-- }}} -->

* Autocomplete support:
<!-- {{{  -->

    ```
    sudo pip install argcomplete
    sudo activate-global-python-argcomplete
    ```
	
<!-- }}} -->
        
* Using VirtualBox for creating a NATed network in which run a team
  between different VirtualBox guests:
<!-- {{{  -->

	Run:

    ```
    VBoxManage natnetwork add -t localnet -n "192.168.15.0/24" -e -h on
    ```

<!-- }}} -->

<!-- }}} -->
