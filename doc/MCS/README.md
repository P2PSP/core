Multi-Channel Set of rules
==========================

The P2PSP may broadcast different channels (streams) over distinct
(unconnected) teams and users can run several peers in parallel, one
peer per channel the user wants to receive. The only essential
requirement to enable multi-channel capability is the network
providing sufficient bandwidth. However, when this condition can not
be achieved, users should define the channel priorities. Using this
information and if not enought bandwidth is avaiable, the peer
instances that correspond to the lower priority channels will be
identified as unsupportive peers and rejected from their teams.

To implement that behaviour, the MCS module introduces the
encapsulation scheme:

	\begin{quote}
		[MCS] = [Priority, [DBS]]
	\end{quote}
		
and a new type of node, the Multichannel Scheduler $M$.

Therefore, those peers that implement the MCS must label each DBS
message. This label is a 16-bit positive integer number that
represents a priority, being zero the highest one. MCS messages are
sent to $M$ which basically implements a priority FIFO queue of
messages. Each time a new [MCS] is received by $M$, it sorts them
by priority and next, by chunk number. Thus, if there is not enough
bandwidth to transmit all packets, the user stops receiving those
channels that have been assigned a lower priority.

The MCS module can also be useful when simulcasting, scalable media
coding and multiple description media coding is used. In these
situations, the different channels refeer to different representations
(qualities, resolutions, etc.) of the same media content.
