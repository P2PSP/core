IMS (Ip Multicast Set of rules)
===============================

IMS can be enabled if IP multicast is avaiable for connecting the peers
of the team.

Rules
-----

1.  **Multicast traffic:** The splitter sends the stream (of chunks) to a IP multicast
    address:port (channel), which peers listen to.

2.  **Peer arrival:** Incomming peers contact the splitter in order to join the channel.

3.  **Buffering:** Chunks are enumerated by the splitter and buffered
    in the peers in order to hide the network jitter. In the IMS mode,
    each peer can use a different buffer size. We define:

        IMS_packet = [chunk_index, chunk]

    Each peer can use a different buffer size $B$. By performance
    reasons, it must be hold that

    \begin{equaiton}
      M = pB
      \label{eq:chunk_index_buffer_size_relation}
    \end{equation}

    where $M-1$ is the maximun chunk index and $p$ is a
    positive integer.

4.  **Peer departure:** Nothing to report. 
