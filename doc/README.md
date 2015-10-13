---
title: 'Peer-to-Peer Straightforward Protocol (P2PSP)'
...

P2PSP is an application-layer protocol designed for real-time
broadcasting of data on a P2P overlay network. P2PSP mimics the IP
multicast behaviour, where a source sends only a copy of the stream to a
collection of peers which interchange between them those chunks of data
that are needed for the rest of the peers.

Motivation
==========

Efficient large scale distribution of media (real-time video, for
example) is one of the big challenges of the Internet. To achieve this,
IETF designed IP multicast. In this transmission model, a source sends
only one copy of the stream which is delivered to a set of receivers
thanks to the automatic replication of data in the IP multicast routers.
Unfortunately, IP multicast does not fit the bussines model of most
Internet Service Providers (ISP) which disables this functionality to
end-users.

Related work
============

There are plenty of P2P straeming protocols. Depending on the overhaly
topology, they can be clasified in chains, trees or meshes. A chain
overlay is quite rare because churn can degrade significatively the
Quality of Service (QoS) of the overlay, however, it has interesting
characteristics such as peers does not need to interchange buffer maps
and peers only send a copy of the stream regardless of the size of the
overlay (we will refeer to this characteristics as “replication
factor”). Tree overlays impose that peers must send so many copies of
the stream (replication factor) as the degree of the tree, but like
chains, the protocol is also push-based. Mesh-based protocols are more
flexible regarding the overlay topology (which can be any) but peers
must known the state of the buffer of their neighbours (the protocol is
pull-based), and also are more flexible about the replication factor,
which can be any. Obviously, push-based protocols are more efficient
than pull-based one in terms of bandwidth.

P2PSP is a fully-connected mesh-structured push-based protocol. Being
$N$ the number of peers in the overlay (a “team” in the P2PSP jargon),
$N$ is degree of the mesh. The replication factor in P2PSP is 1 by
default, although as in mesh-based protocolos, it can be any other
depending on the solidarity between the peers.

\# \[IMS (Ip Multicast Set of rules)\](IMS/README.md)
