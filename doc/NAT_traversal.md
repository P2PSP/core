NAT traversal methods
=====================

## NAT traversal in P2PSP protocol
Information about NAT traversal in the P2PSP protocol can be found in the
[P2PSP protocol documentation][1] and in [this slideshow][2].
This document documents the NAT traversal methods developed in the GSoC 2015
project "NAT traversal using UDP hole punching".

## NAT types
The behaviour of different implementations of NAT devices (i.e. routers), can be
grouped into a few different NAT types. A short description from [this page][3]:

* **Full-cone NAT (FCN):**
"A full-cone NAT is one where all requests from the same internal IP address
and port are mapped to the same external IP address and port. Any external
host can send a packet to the internal host simply by sending a packet to the
mapped external address."

* **Restricted cone NAT (RCN):**
"A restricted-cone NAT is one where all requests from the same internal IP
address and port are mapped to the same external IP address and port. Unlike a
full-cone NAT though, an external host can send a packet to the internal host
only if the internal host had previously sent a packet to that external host."

* **Port-restricted cone NAT (PRCN):**
"A port-restricted cone NAT is like a restricted-cone NAT, but the restriction
also includes port numbers. An external host can send a packet to the internal
host only if the internal host had previously sent a packet to that external
host on the same port number."

* **Symmetric NAT (SYM):**
"A symmetric nat is a NAT where all requests from the same internal IP address
and port to a specific destination IP address and port are mapped to the same
external source IP address and port. If the same internal host sends a packet
with the same source address and port to a different destination, a different
mapping is used (these mappings are referred to as NAT translations). Only the
external host that receives a packet can send a packet back to the internal
host."

As described in [this paper][4], the symmetric NATs can be divided again into
these subtypes, depending on the allocation of the source port of the NAT:

* **Port preservation (SYMPP):**
The public source port of the NAT is the same as the source port of the local
host. If this NAT behaviour is detected, prediction of the public port is
trivial.

* **Sequential port allocation (SYMSP):**
To allocate a new public source port, the next free port number is selected, so
the port number is incremented each time. This behaviour is covered by the P2PSP
NTS of rules in algorithms 5 and 6.

* **Random port allocation (SYMRP):**
For each new pair `(dest. address, dest. port)` a completely random public
source port is selected. A connection between two peers each behind this NAT
type cannot be established, as each other's public source port is unpredictable.

[1]: http://p2psp.org/en/p2psp-protocol?cap=indexsu9.html
[2]: http://slides.p2psp.org/BCN-2015
[3]: https://wiki.asterisk.org/wiki/display/TOP/NAT+Traversal+Testing
[4]: https://tools.ietf.org/id/draft-takeda-symmetric-nat-traversal-00.txt
