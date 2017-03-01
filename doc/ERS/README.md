Error Resilience Set or rules
=============================

Due to different reasons, peer can lost chunks. This set of rules propose a distributed mechanism recovery for missing chunks.

### Rule 1: Peers share with the rest of the team the modifications in their list of peers

When a peer $P_i$ removes a peer $P_j$ from his list of peers because $P_j$ is impolite, $P_i$ sends to the rest of peers of his list of peers the event, using piggybacking (concatenated with the chunk received from the splitter). This action will be repeated (always using piggybacking) while the corresponding peer does not acknowledge the reception.

### Rule 2: Peers track which peer relayed each received chunk

This allows to know which chunk was sent from the splitter to $P_j$.

### Rule 3: A peer sends the lost chunks to $P_i$

Each peer that has a good relationship with $P_j$ (notice that thanks to the Rule 1, all peers of the team know who should receive from $P_j$) builds a set of peers $H$ sorted by IP:port with the peers that have a good relationship with $P_j$. Thus, the $k$-th peer of $H$ will send the received chunk from $P_j$ to $P_i$ if

    \begin{equation}
      #C % k == 0
    \end{equation}
    
where `#C` is the chunk number received from $P_j$.

<!-- Multiple splitters transmitting the same stream can improve the
performance in contexts where the lost of chunks is quite high.-->

