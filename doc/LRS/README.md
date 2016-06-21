LRS (Lost-chunk Recovery Set of rules)
======================================

The P2PSP relies on the UDP as the transport protocol and, obviously,
packet losses can happen. The impact of a packet loss in the
[QoS](https://en.wikipedia.org/wiki/Quality_of_service) offered by the
team depends on where the packet is lost. If the packet is lost in its
trip between the splitter and a peer, this packet will be missed by
all the peers of the team, included the monitor peers. However, if the
packet is loss in the trip between two peers, only the destination
peer will loss the chunk.

Only monitor peers tell the splitter which chunks have not been
received on time. More specifically, a monitor peer $P$ sends to the
splitter a [lost chunk index $x$] loss-report message when a chunk
with chunk-number $x$ has been lost. Using this information, the
splitter can enumerate the number of times that a chunk has been
lost. In this framework, the LRS module defines that the splitter
resend a lost chunk stored in the location $x~\text{mod}~M$ of its
buffer of chunks if the number of losses is equal to the number of
monitor peers. The selected peer to resend this block will be one of the
monitor peers.

Notice also that, in this case, monitor peers should become aware of a
chunk loss some time before of that the rest of peers of the team send
it to their players, in order to have enough time to resend the lost
chunk from the monitor peer to the rest of peers of the team. A simple
technique that has been proven to work is to use in the monitor peers
a buffer size with the half the size of the buffer size of the rest of
peers. Thus, when a monitor peer realizes that a chunk has been lost,
the rest of peers should be receiving this chunk and inserting it
approximately in the middle of their buffers and the resent chunks
should be received just on time. Therefore, the buffer size must hold
that

	\begin{equation}
		B \leq 2|T|
		\label{eq:buffer_size_peers_LRS}
	\end{equation}

if LRS is used and the buffer size of monitors peers is B/2.

Rules
-----

1.  **Loss-report messages generation:** Monitors peers send

		[loss chunk index $x$]

	messages to the splitter if chunk $x$ has been lost (see rule
    [**Chunk tracking at the splitter **](../DBS/README.md)).

2.  **Chunk retransmission:** If a number of '[loss chunk index $x$]'
    equal to the number of monitors has been received at the splitter,
    it resend the chunk stored in the position

		$x~\text{mod}~M$

	of its buffer, being $M-1$ the maximun chunk index.

