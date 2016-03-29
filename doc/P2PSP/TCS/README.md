Team Clustering Set of rules
============================

All peers of a team have the same buffer size, which depends on the
number of peers of the team. Therefore, the size of the team must be
limited at configuration time of the team.

The entity in charge of controlling the configuration (which peer will
be part) of the teams is the tracker. An incomming peer should first
contact the tracker that will specify to the peer a team by means of a
splitter (each team has a different splitter). The policy used for the
tracker to decide which team will be assigned should fulfill the
maximun buffer size constraint. Other factors such as the physical
network topology or the packet loss ratio of the incomming peer in the
pass could be also considered. For example, if a peer was rejected
from a team because is selfish, a less demanding team could be
assigned. A time-line describing the attaching process is presented next:

```
Tracker       Peer        Splitter
   |            |            |
   |<---Hello---+            |
   +--Splitter->|            |
   |            +---Hello--->|
   |            |<---List----+
   |            |            |


The attaching process of a peer to a team.
```

The logical topology used to interconnect the splitters between
themselves depends on the local capacity of the network. Some 0-level
splitters could receive the signal directly from the 0-level source
while a 1-level splitter will be attached to 0-level peer.

The latency of a team is proportional to the team size (the number of
peers in the team). Therefore, we can say that the latency is $|T|$
units of time, where $T$ is the set of peers of the team and $|\cdot|$
is the cardinality operator. Lets suppose that the source have enough
bandwidth to send up to $|T|$ replicas of the stream. In this case, it
could be achieved that $|T|=1$. In the opposite case, if the source is
able to send only one copy of the stream, the replication must be
performed by the peers and the latency for all peers of the team is
$|T|$.
