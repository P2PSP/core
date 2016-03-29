# Content Integrity Set of rules

## STrPe (Strategy based on Trusted Peers)

STrPe is a simple approach with a low data overhead in the overall operation of the team. The only difference with respect to an pollution-unaware P2PSP system is an extension of the splitter functionality and the inclusion of anonymous trusted peers (TP) who transparently monitor the behavior of regular peers in the team. Regular peers see a TP as another regular peers.

In current implementation, there are 2 variants of STrPe available:
- TP sends every X chunk to check, where X is a random value, based on team size
- TP sends every received chunk to check

Splitter checks chunks only from messages received from TP (so Bad Mouth attack cannot be performed).

To run team with STrPe enabled you can use these commands:
```
$ cd path/to/p2psp/src
$ vlc Big_Buck_Bunny_small.ogv --sout "#duplicate{dst=standard{mux=ogg,dst=,access=http}}" & # run stream
$ ./splitter.py --source_port 8080 --strpe “127.0.0.1:56000” --checkall # run splitter and set one TP with option
$ ./peer.py --use_localhost --trusted --port 56000 # run TP (which also is monitor peer)
$ vlc http://localhost:9999 &
$ ./peer.py --use_localhost --player_port 10000 # run simple peer
$ vlc http://localhost:10000 &
```

## STrPe-DS (Strategy based on Trusted Peers and Digital Signatures)

STrPe-DS is an extension of the first one, where a digital signature of a chunk allows to detect attackers. STrPe-DS generates more data overhead than STrPe but the performance of the defense mechanism is greatly improved.
Overhead for chunk messages is near 10% since we have to send additional data with chunk - the sign of message.

Overhead for chunk messages is near 10% since we have to send additional data with chunk - the sign of message.

Every T seconds splitter requests one peer from team (consequently) and one TP (also, consequently) for their lists of malicious peers. If TP responses, then splitter remove that peer from the team. Also, majority decision is enabled and ratio equals 50% (in other words, if more than 50% of peers responses that peer P is malicious, then splitter remove it from team).

To run team with STrPe-DS enabled you can use these commands:
```
$ cd path/to/p2psp/src
$ vlc Big_Buck_Bunny_small.ogv --sout "#duplicate{dst=standard{mux=ogg,dst=,access=http}}" & # run stream
$ ./splitter.py --source_port 8080 --strpeds “127.0.0.1:56000” # run splitter and set one TP
$ ./peer.py --use_localhost --strpeds --port 56000 # run TP (which also is monitor peer)
$ vlc http://localhost:9999 &
$ ./peer.py --use_localhost --strpeds --player_port 10000 # run simple peer
$ vlc http://localhost:10000 &
```

## Malicious peers
Also, during the project there was implemented several types of attack to test effiency of STrPe and STrPe-DS mechanisms. Here they are:
- Persistent attack
- On-off attack
- Selective attack
- Bad-mouth attack (only for STrPe-DS)

To run persistent attack you can use:
```
$ ./peer.py --use_localhost --strpeds --player_port 10000 --malicious --persistent
```
To run on-off attack you can use:
```
$ ./peer.py --use_localhost --strpeds --player_port 10000 --malicious --on_off_ratio 40
```
where 40 is a coefficient for chances to send poisoned chunk (40%).

To run selective attack you can use:
```
$ ./peer.py --malicious --selective "127.0.0.1:56000"
```
Malicious peer will send poisoned chunks only to that peer.

To run bad-mouth attack you can use:
```
$ ./peer.py --strpeds --malicious --bad_mouth "127.0.0.1:1234" "127.0.0.1:4321"
```
Malicious peer will complain on given peers.
