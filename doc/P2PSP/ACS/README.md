ACS (Adaptive Chunk-rate Set of rules)
======================================

All nodes of a team (peers and splitter) that implements only the DBS
must transmit exactly the same amount of media (this basically implies
that if a peer can not fulfill this requirement it will be thrown of
the team). Unfortunately, this could be considered too much demanding
in some specific configurations, such as a team of colleagues that
want to share a content regardless of who spends more transmission
bandwidth, or in PPV (Pay-Per-View) systems where the stream must be
guaranteed to those users that have paid for receiving the stream.

The number of chunks that ultimately a peer must retransmit depends
exclusively on the number of chunks that the peer receives from the
splitter. Besides, the splitter knows the transmission performance of
the peers by checking the number of times that the peers has lost a
chunk (see [LRS](../LRS/README.md)). This knowledgment could be
exploited by the splitter to maximize the profiting of the team
capacity by assigning a different chunk-rate to the
peers depending on their reliability. In other words, if a peer does
not loss chunks, then its chunk-rate will be increased and
viceversa.

Now, lets classify the peers into two types: (1) class-A peers, that
contribute more, and (2) class-B peers, that contribute less. By
default and using only ACS, the chunk-rate per peer will be the same
for all peers. In this framework, ACS proposes an adaptive
Round-Robing scheduler (at the splitter) in which the team cicle of a
peer P is proportional to the packet loss ratio of P. Using ACS, a
class-A peer will receive from the splitter more chunks than a class-B
peer and therefore, a class-A peer will enter in the burst mode (see
the rule [**Burst transmission**](../DBS/README.md)) more often than a
class-B peer. This is something that goes against the throughtput of
the class-A peer and that, in some moment, could produce a lost of
chunks (remember that the burst mode can congest the upload channel of
the peers). Therefore, the throughtput of a class-A peer will grow
until reaching its congestion threshold, instant in which the monitors
peers will report the lost of this class-A peer and the splitter will
decrease its chunk-rate.

Another consecuence of implementing ACS is that class-A peers will
remove from their list of peers to class-B peers more often, with a
frequency that depends on among other things of the 'MAX_LOSS_COUNTER'
configuration parameter of each peer. However, this action has not a
noticeable impact on the performance of the team because the time that
lasts from that a class-A peer removes a class-B peer of its list of peers
is smaller than the time that the class-B peer needs to send a chunk
to the class-A peer, and when this happens, the class-B peer is
inserted again in the list of peers of the class-A peer, reseting its
loss counter. Anyway, an increment of the \texttt{MAX\_LOSS\_COUNTER}
in class-A peers would improve the performance of the system.

Rules
-----

1.  **Dynamic Round-Robing scheduling:** Depending on the packet
    loss-ratio of the peers, the splitter changes the packet-ratio of
    the peers.

