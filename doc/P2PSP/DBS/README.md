DBS (Data Broadcasting Set of rules)
===============================

DBS emulates IMS behaviour when
[IP multicast](https://en.wikipedia.org/wiki/IP_multicast) it not
available.


Rules
-----

1.  **Chunk scheduling:** The splitter sends the stream (of chunks) to
	the peers using using a
	[Round-Robing scheduling](https://en.wikipedia.org/wiki/Round-robin_scheduling)
	and
	[unicast transmissions](https://en.wikipedia.org/wiki/Unicast).
	The splitter sends the $n$-th chunk to the peer P$_i$ if
	
    \begin{equation}
	  (i+n) \bmod |T| = 0, \label{eq:bdist}
    \end{equation}

    where $|T|$ is the number of peers in the team. Next, P$_i$ must
    forward this chunk to the rest of peers of the team. Chunks
    received from other peers are not retransmitted.

2.  **Congestion avoidance in peers:** Each peer sends the chunks that
	have been received from the splitter using a constant bit-rate
	strategy to minimize the congestion of its uploading link. Notice
	that the rate of chunks that arrive to a peer is a good metric to
	perform this control in networks with a reasonable low packet loss
	ratio.

3.  **Burst transmission:** The congestion avoidance mode is
	immediately abandoned if a new chunk has been received from the
	splitter before the previous chunk has been retransmitted to the
	rest of peers of the team. In the burst mode the peer sends the
	previously received chunk from the splitter to the rest of peers
	of the team as soon as possible. In other words, the peer sends
	the previous chunk to the rest of peers of the list (of peers) as
	faster as it can. Notice that although this behaviour is
	potentially a source of congestion, it is expectable a small
	number of chunks will be sent in the burst mode under a reasonable
	low packet-loss ratio.

4.  **The list of peers:** Every node of the team (splitter and
	peers) knows the endpoint P=(P.IP_address, P.port) of the rest of
	peers in the team. A list is built with this information which is
	used by the splitter to send the chunks to the peers and is used
	by the peers to forward the received chunks to the other peers.

5.  **Peer arrival:** An incoming peer P must contact with the
    splitter in order to join the team. After that, the splitter sends
    to P the list of peers and the current stream header over the
    TCP.

	More exactely, the splitter does:

	1.  Send (over TCP) to P the number of peers in the list of peers.

	2.  For each peer P$_i$ in the list of peers:

	    1. Send (TCP) to P the $P_i$ endpoint.

	3.  Append P to the list of peers.

	Incomming peers P perform:

	1.  Receive (TCP) $|T|$ from the splitter.

    2.  For each peer P$_i$ in the list of peers:
		1.  Receive (TCP) end endpoint P$_i$ from the splitter.
        2.  Send (UDP) to $P_i$ a [hello] message.

	Because [hello] messages can be lost, some peer of the team could
	not meet P in this presentation. However, because peers also learn
	about their neighbors when a [[IMS] message](../IMS/README.md) is
	received, the impact of these losts should be small.

5.  **Free-riding control in peers:** The key idea in the DBS is that
	in a large enough interval of time, any peer should retransmit the
	same amount of data that it receives. If a (infra-solidary) peer
	can not fulfil this rule, it must leave the team and maybe join a
	less-demanding (in terms of bandwidth) team. In order to achieve
	this requirement, each peer P$_i$ assigns a counter to each other
	peer P$_j$ of the team. When a chunk is sent to P$_j$, its counter
	/P$_j$/ is incremented and when a chunk is received from it,
	/P$_j$/ is decremented. If /P$_j$/ reaches a given threshold
	('MAX_CHUNK_COUNTER'), P$_j$ is deleted from the list of peers of
	P$_i$ and it will not be served any more by P$_i$.

	Notice that this rule will remove also from the peer's lists those
	peers that perform a impolite churn (peers that leave the team
	without sending the [goodbye] message).

6.  **Monitor peers:** Some peers, which usually are close (in
	hops) to the splitter, play different roles depending on the P2PSP
    rules implemented. Among others:
	
    1.  As a consequence of the impolite churn and peer insolidarity,
		it is unrealistic to think that a single video source can feed
		a large number of peers and simultaneously to expect that the
		users will experience a high
		[QoS](https://en.wikipedia.org/wiki/Quality_of_service). For
		this reason, the team adminitrator should monitorize the
		streaming session because, if the media is correctly played by
		the monitor peer, then there is highly probable that the peers
		of the team are correctly playing the media too.

	2.  At least one monitor peer is created before any other peer in
		the team and for this reason the transmission rate of the first
		monitor peer is $0$. However, the transmission rate of the second
		(first standard) peer, and the monitor peer, is:

	    \begin{displymah}
           B/2,
        \end{displaymath}
		   
        where $B$ is the average encoding rate of the stream. When the
        size of the team is $|T|$, the transmission rate of all peers
        (included the monitor peers, obviously) of the team is:

	    \begin{equation}
          B\frac{|T|}{|T|+1}.
        \end{equation}
		  
	    Therefore, only the first (monitor) peer is included in the team
        without a initial transmission requirement. Notice also that

	    \begin{equation}
		  \lim_{|T|\rightarrow\infty}B\frac{|T|}{|T|+1}=B,
        \label{eq:bit-rate-limit}
        \end{equation}
		
		which means that when the team is large enough, all the peers
		of the team will transmit the same amount of data that they
		receive.

	3.  In order to minimize the number of loss reports (see the rule
		**Loss-report messages generation**, in [LRS](../LRS/README.md))
		in the team, the monitor peers are the only entities allowed to
		complain to the splitter about lost chunks.

7.  **Peer departure:** Peers are required to send a [goodbye]
	message to the splitter and the rest of peers of the team when they
	leave the team, in order the splitter stop sending chunks to
    them as soon as possible. However, if a peer P$_i$ leaves without
	warning no more chunks will be received from it. This should
	trigger the following succession of events:

	1.  In the rest of peers $\{P_j, i\neq j\}$, the free-riding
		control mechanism (see the rule **Free-riding control in the
		peers**) will remove $P_i$ from the list of peers.
		
    2.  All monitor peers will complain to the splitter about chunks
		that the splitter has sent to P$_i$.
	
    3.  After receiving a sufficient number of complains, the splitter
        will delete P$_i$ from his list.

8.  **Relation between the buffer size $B$ and the team size $|T|$:**
	As in IMS, peers need to buffer some chunks before starting the
	playback. However, the main reason of buffering in DBS is not the
	network jitter but the team jitter. As it has been defined in the
	rule **Chunk scheduling**, peers retransmit IMS messages (the
	format of the messages in IMS and in DBS is the same) received
	from the splitter to the rest of the team. Also, it has been
	specified in the rule **Congestion avoidance in peers** that peers
	send these messages using the chunk-rate of the stream. Therefore,
	depending on the position of a peer P$_i$ in the list of peers of
	the peer P_$j$, it can last more or less chunk times for P$_j$
	sending the IMS message to P$_i$.

	In order to handle this unpredictable retransmission delay, the
	peer's buffers should store at least $|T|$ chunks. This means
	that, the team size is limited by the buffer size, i.e., in the
	DBS module it must be hold that

    \begin{equation}
      |T| \leq B.
    \end{equation}

9.  **Chunk tracking at the splitter:** In order to identify
    unsupportive peers (free-riding), the splitter remembers the
    numbers of the sent chunks to each peer among the last $B$
    chunks. Only the monitor peers will complain about a lost chunk
    $x$ to the splitter using [lost chunk number $x$] complain
    messages. In DBS, a chunk is clasiffied as lost when it is time to
    send it to the listener (player) and the chunk is missing.

10. **Free-riding control in the splitter:** In DBS, peers must
    contribute to the team the same amount of data they receive from
    the team (always in the conditions imposed by the
    Equation~\ref{eq:bit-rate-limit}). In order to guarantee this, the
    splitter counts the number of complains (sent by the monitor(s)
    peer(s)) that each peer produces. If this number exceeds a given
    threshold, then the unsupportive peer will be rejected from the
    team (it will be removed from the list of the splitter and the
    lists of all peers of the team (see the rule **Free-riding control
    in the peers**).
