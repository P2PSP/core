Running a team between different VirtualBox guests
==================================================

1. Create a "NAT Network":

    ```
    VBoxManage natnetwork add -t localnet -n "192.168.15.0/24" -e -h on
    ```

2. In the "Splitter" machine:

    1. Run the source (see VLC.md).

    2. Run the splitter:

       ```
       ./splitter.py --source_port 8080
       ```

    3. Run the monitor:

       ```
       ./peer.py --splitter_host 192.168.15.4
       ```

    4. Run the monitor's player:

       ```
       vlc http://localhost:9999 &
       ```

2. In the "Peer" machine:

   1. Run the peer:

      ```
      ./peer.py --splitter_host 192.168.15.4
      ```

   2. Run the peer's player:

      ```
      vlc http://localhost:9999 &
      ```

