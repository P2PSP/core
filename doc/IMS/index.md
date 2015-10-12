IMS (Ip Multicast Set of rules)
===============================

IMS can be enabled if IP multicast is avaiable for connecting the
peers of the team.

# Rules

1. The splitter sends the stream (of chunks) to a IP multicast
address:port (channel), which peers listen to.

2. Incomming peers contact the splitter in order to join know the
channel.

3. Chunks are enumerated by the splitter and buffered in the peers in
order to hide the network jitter. We define:

	```
	IMS_packet = [chunk_number, chunk]
	```

Each peer can use a different buffer size $B$. The relation between the buffer size and the maximun chunk number is

