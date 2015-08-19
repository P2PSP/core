NAT traversal testing
=====================

This document shows detailed information about the test network setup used to
test NAT traversal between two P2PSP peers, each behind a NAT. General
information about the test can be found [here](NAT_traversal_testing.md).

## Network setup
The setup with network interfaces and IP addresses as used in the tests is shown
in the following diagram:

![network setup details](images/network_setup_details.png)

On a Linux machine with network namespaces, the network can be automatically set
up by running [this script](../tools/setup_NAT_network.sh) as root. The network
can also be set up using virtual machines for each host in the diagram.

## NAT types
To test the behaviour of peers behind different kinds of NAT devices (i.e.
routers), different NAT types are simulated. The characteristics of each type is
described in [this document](NAT_traversal.md). The different NAT types are
configured by the iptables in [this directory](iptables/).

### SYMSP workaround
If iptables is configured like [this](iptables/iptables.rules.symsp1), then UDP
packets **by different sockets to the same destination** will each have an
incremented source port, else the mapping would be ambiguous. Now if any number
of sockets connect to different destinations, for each it uses the same source
port, because the mapping is not ambiguous. A sequentially port allocating
symmetric NAT (SYMSP) however increments the source port in the latter case.

To achive the desired behaviour, the [`symsp_socket`](../src/symsp_socket.py)
and [`symsp_peer`](../src/symsp_peer.py) classes force the NAT to allocate a new
port by the following workaround:

* The peer connects to destination A; source port P is allocated.
* The peer now wants to connect to the new destination B; the `symsp_socket`
  class creates a new temporary socket and connects this to B. Because of a new
  socket to a new destination, source port P is allocated again, as there is
  no ambiguity with other mappings.
* Now the `symsp_socket` class connects the original socket to B, and because
  port P is already used by another socket, source port P+1 is allocated.

This is done for each new destination, so for destination C the `symsp_socket`
class would force the NAT to allocate source port P+2. To simulate higher port
steps, more temporary sockets are created and connected to the new destination,
before being closed right after.
