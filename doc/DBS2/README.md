
DBS2 (Data Broadcasting Set of rules)
====================================

```diff
-(Not Implemented)-
```

DBS2 is a generalization of DBS.

The following rules overwrite the corresponding rule in DBS.

Rules
-----

2. **Chunk scheduling at the peers:**  In this set of rule a peer can forward all those chunks that it received from splitter ( for which this peer is origin) and it can also forward all those chunks that are received from other peers (for which this peer is not an origin).

	Each peer has a forwarding table with the structure:
	```
	  forwading_table{
	    X: [.....,Z,.....]
	    Y: [.....,Z',....]
	    .
	    .
	    .
    }
    ```

P<sub>i</sub> is origin of a chunk if it receive this chunk directly from the splitter.

**Forwarding Rules:**
When a peer P<sub>i</sub> receives a chunk originated at P<sub>k</sub>, it forwards this chunk to each peer P<sub>z</sub> in forwarding list of P<sub>k</sub> of its forwarding table .
e.g.    forward[ P<sub>k</sub> ] = [ ........, P<sub>z</sub> ,.........] 

When a chunk is received from splitter then P<sub>k</sub> = P<sub>i</sub>.

**Generation of forwarding table:**   
A forwarding table for a peer is generated following way:
* Initially forwarding table have only one entry correspond to peer P<sub>i</sub> itself with empty list.
* Forwarding list of a peer P<sub>i</sub> is populated when it :
	* receives a chunk from other peer.
	* receives hello message from other peer.
*  When a peer P<sub>i</sub> receives a chunk request from the peer P<sub>j</sub> for a chunk originated at P<sub>k</sub> then peer P<sub>j</sub> is appended to the forwarding list of P<sub>k</sub> in the forwarding table.

