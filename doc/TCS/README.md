Team Clustering Set of rules
============================

```diff
-(Not Implemented)-
```
In a typical P2PSP configuration, a source (such as an Icecast server) sends a stream X (a channel) to a set of splitters S={S_1, ..., S_n}. All these splitters are basically broadcasting the same stream, with a small time offset among them.

When an incoming peer P_i wants to join a team, P_i must pick a splitter in S. In this situation, a tracker T is an entity in charge of selecting the most convenient splitter for P_i. So, the first P_i must contact T, T will select an S_j and them, P_i will contact S_j. In a timeline:

```
[T]racker   [P]eer[_i]  [S]plitter[_j]
   |            |            |
   |<---Hello---+            |
   +--Splitter->|            |
   |            +---Hello--->|
   |            |<---List----+
   |            |            |


The attaching process of a peer P_i to a team S_j.
```

In P2PSP, the main "signal" latency that a peer experiments is caused by the number of chunks that such peer must buffer before it starts to play the stream. It also holds that the buffer size (in chunks) must be equal to the number of peers in the team. Therefore, if N is the number of peers in a team, a delay proportional to N will be generated. In this context, the tracker T should provide load balancing among the teams in order to minimize the variance of the delay produced by the buffering.

Another important task that should be provided at this set of rules is that the different splitters that are retransmitting a stream should be synchronized. In this way, all splitters in S should include exactly the same data in the same chunks. In other words, if we have two splitters S_* and S_^, both transmitting the same channel, two chunks C*_i and C^_i (where i is the chunk number) should have exactly the same stream content.
