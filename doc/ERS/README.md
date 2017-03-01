Error Resilience Set or rules
=============================

Due to different reasons, peer can lost chunks. This set of rules propose a distributed mechanism recovery for missing chunks.

### Rule 1: Peers share with the rest of the team the modifications in their list of peers

When a peer $P_i$ removes a peer $P_j$ from his list of peers because $P_j$ is impolite, $P_i$ sends to the rest of peers of his list of peers the event, using piggybacking (concatenated with the chunk received from the splitter). This action will be repeated while the corresponding peer does not acknowledge the reception.

### Rule 2: Peers track which peer relayed each received chunk

This allows to know which chunks was sent from the splitter to $P_j$ (and also, to $P_i$).

### Rule 3: One (or more) peer(s) send(s) the lost chunks to $P_i$



Therefore, the peers know 

Multiple splitters transmitting the same stream can improve the
performance in contexts where the lost of chunks is quite high.

