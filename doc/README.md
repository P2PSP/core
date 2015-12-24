Peer-to-Peer Straightforward Protocol (P2PSP)
=============================================

An application-layer protocol for real-time multicasting of data from
a source to a set of networked entities (peers).

[Multicasting](https://en.wikipedia.org/wiki/Multicast)
-------------------------------------------------------

A (scalable) communication model where a source of information can send data to a collection of destinations.

![](https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Multicast.svg/250px-Multicast.svg.png)

[IP multicast](https://en.wikipedia.org/wiki/IP_multicast)
----------------------------------------------------------

On the Internet, multicasting can be performed with IP multicast,
where the network infrastructure
[Routers](https://en.wikipedia.org/wiki/Router_(computing)) are in
charge of replicating data.

Availability of IP multicast
----------------------------

Plain users can not use IP multicast if the source and destinations are in different [LANs](https://en.wikipedia.org/wiki/Local_area_network). The main reasons:

1. Sources (usually content providers) can not control how many times the media is replicated and where it is delivered.
2. [IP multicast can be used to perform DoS attacks.](https://tools.ietf.org/html/rfc4732#section-2.2.2)
3. [ISPs](https://en.wikipedia.org/wiki/Internet_service_provider) are not able to measure the cost of the IP multicast traffic and therefore, can not charge that to the sources.

[Aplication Layer Multicast](https://en.wikipedia.org/wiki/Multicast#Application_layer_multicast)
-------------------------------------------------------------------------------------------------

Multicasting can be provided using (application level) alternatives to IP (network level) multicast. The most used:

1. [Content delivery networks](https://en.wikipedia.org/wiki/Content_delivery_network).
2. [P2P overlays](https://en.wikipedia.org/wiki/Peercasting).

[P2P systems](https://en.wikipedia.org/wiki/Peer-to-peer)
---------------------------------------------------------

Depending on the topology of the overlay network, P2P systems can be classified in chains, trees or
meshes.

Chain overlays are quite rare because [churn](https://en.wikipedia.org/wiki/Churn_rate) can degrade
significatively the [Quality of Service (QoS)](https://en.wikipedia.org/wiki/Quality_of_service) provided. However,
it has interesting characteristics such as peers does not need to
interchange information about the availability of the stream, and therefore, it can be transmitted using a *push-based protocol* and peers only send one copy of the stream
regardless of the size of the overlay (we will refeer to this
characteristic as the *replication factor*).

Tree overlays impose that
peers must send so many copies of the stream (replication factor) as
the degree of the tree, but like chains, the protocol is also
push-based.

Mesh overlays are more flexible regarding the
overlay topology and the replication factor. However, pull-based protocols (that are less efficient in terms of bandwidth and latency than push-based ones) are usually necessary.

Definition
----------

P2PSP is 

P2PSP mimics
the IP multicast behaviour, where a data source sends only a copy of the
stream to a the peers. However, differently to IP multicast where the routers replicate the chunks as many times as receivers, in P2PSP the peers are in charge of this task: peers must send to the rest of peers those chunks that have been received from the splitter.

Motivation
----------

Efficient large scale distribution of real-time media (video, for
example) is one of the big challenges of the Internet. To achieve this (among other thigs),
[IETF](https://www.ietf.org/) designed IP multicast. In this transmission model, a source sends
only one copy of the stream which is delivered to a set of receivers
thanks to the automatic replication of data in the IP multicast routers.
Unfortunately, IP multicast does not fit the bussines model of most
Internet Service Providers (ISP) which disables this functionality to
end-users.

Icecast technology
------------------

[Icecast](http://icecast.org/) is an open-source media server of
[Theora](http://www.theora.org/), [Vorbis](http://www.vorbis.com/),
[Opus](https://www.opus-codec.org/),
[MP3](https://en.wikipedia.org/wiki/MP3) and
[WebM](http://www.webmproject.org/) streams. The following figure
shows an example of a Icecast streaming system:

![A Icecast overlay][images/icecast-model]

Icecast + P2PSP technology
--------------------------

Basically, P2PSP extends Icecast overlays in order to decrease the
load of the server (Source) side, generating hybrid Icecast+P2PSP
structures that are more scalable. The following figures shows
examples of this concept:

![A Icecast+P2PSP overlay][images/icecast-P2PSP-model1]
![A Icecast+P2PSP overlay][images/icecast-P2PSP-model2]





P2PSP is a fully-connected mesh-structured push-based protocol. Being
$N$ the number of peers in the overlay (a “team” in the P2PSP jargon),
$N$ is degree of the mesh. The replication factor in P2PSP is 1 by
default, although as in mesh-based protocolos, it can be any other
depending on the solidarity between the peers.

[IMS (Ip Multicast Set of rules)](IMS/README.md)
------------------------------------------------
[DBS (Data Broadcasting Set of rules)](DBS/README.md)
-----------------------------------------------------
[LRS (Lost Recovery Set of rules)](LRS/README.md)
-------------------------------------------------
[ACS (Adaptive Chunk-rate Set of rules)](ACS/README.md)
-------------------------------------------------------
