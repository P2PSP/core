DBS2 (Data Broadcasting Set of rules)
====================================

```diff
-(Not Implemented)-
```

DBS2 is a generalization of DBS.

The following rules overwrite the corresponding rule in DBS.

Rules
-----

2. **Chunk scheduling at the peers:** When a peer $, which not
    necessary need to be the rest of the team. For example, the
    following team:

	```
	P$_1$ ---- P$_2$ ---- P$_3$
	```

	P$_1$ does not communicate with P$_3$ and viceversa. Therefore, P$_1$
	and P$_3$ are not neighbours.

	Each peer has a routing table with the structure:

	```
	struct Peer {
	  IP_addr destination_peer;
	  IP_addr neighbour_peer;
	  integer number_of_hops;
    };
	  
    struct Routing_table {
	  struct Peer[|T|];
	};
    ```
	
	For example, for the previous team:

	* P$_1$.Routing_table = {{P$_1$,P$_1$,0},{P$_2$,P$_2$,1},{P$_3$,P$_2$,2}}.
	* P$_2$.Routing_table = {{P$_1$,P$_1$,1},{P$_2$,P$_2$,0},{P$_3$,P$_3$,1}}.
	* P$_3$.Routing_table = {{P$_1$,P$_2$,2},{P$_2$,P$_2$,1},{P$_3$,P$_3$,0}}.

	When a peer receives a chunk from the splitter, it forwards this
    chunk to the rest of its neighbours (flooding). In general, a
    P$_i$ which receives a chunk originated in (which means that the
    splitters sends to) P$_k$, sends a chunk to all its neighbours
    P$_j$ if and only if, in P$_j$.Routing_table P$_i$ is in the
    shortest path between P$_j$ and P$_k$.

	For example, for the previous team, the following sequece of events are generated:

	1. The splitter sends a chunk to P$_1$.
	2. P$_1$ floods the chunk towards P$_2$.
	3. P$_2$ "requests" to P$_3$ its routing table P$_3$.Routing_table
       and finds out that P$_2$ is in the shortest path between P$_3$
       and P$_1$ (the peer origin). Therefore, P$_2$ forwards the
       chunk to P$_3$.

12. **Generation of the routing tables:** The routing tables can be
    populated by using the
    [Bellman-Ford Algorithm](https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm). Note
    that the routing tables can be transmitted using piggybacking,
    with the chunks to reduce the overhead.  Note also that, in the
    case of using the Bellman-Ford Algorithm, peers do no need to
    request the routing tables to their neighbours in order to run
    Rule 11, because each peer receives the routing tables of their
    neighbours throughout the execution of the algorithm.
