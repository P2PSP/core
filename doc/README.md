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
([routers])(https://en.wikipedia.org/wiki/Router_(computing)) is in
charge of replicating data.

Availability of IP multicast
----------------------------

In general, plain users can not use IP multicast if the source and
destinations are in different
[LANs](https://en.wikipedia.org/wiki/Local_area_network). The main
reasons are:

1. Sources (usually content providers) can not control how many times
   the media is replicated and where it is delivered.
2. [IP multicast can be used to perform DoS attacks.](https://tools.ietf.org/html/rfc4732#section-2.2.2)
3. [ISPs](https://en.wikipedia.org/wiki/Internet_service_provider) are
   not able to measure the cost of the IP multicast traffic and
   therefore, can not charge the rates to the sources.

[Aplication Layer Multicast](https://en.wikipedia.org/wiki/Multicast#Application_layer_multicast)
-------------------------------------------------------------------------------------------------

Multicasting can be provided (at application level) using alternatives
to IP (network level) multicast. The most used techniques are:

1. [Content delivery networks](https://en.wikipedia.org/wiki/Content_delivery_network). 
2. [P2P systems](https://en.wikipedia.org/wiki/Peercasting).

[P2P systems](https://en.wikipedia.org/wiki/Peer-to-peer)
---------------------------------------------------------

Depending on the topology of the P2P [overlay network](https://en.wikipedia.org/wiki/Overlay_network), P2P systems can be
classified into three categories:

1. Chains. Chain overlays are quite rare because [churn](https://en.wikipedia.org/wiki/Churn_rate) can degrade
significatively the [Quality of Service (QoS)](https://en.wikipedia.org/wiki/Quality_of_service). However,
it has interesting characteristics such as peers does not need to request (explicitly) the chunks of data from their neighbors (this type of protocolos are called *push-based protocol*), peers only send one copy of the stream
regardless of the size of the overlay (we will refeer to this
characteristic as the *replication factor* $R$) and finally, although the chunks are not reordered by the protocol itself and the peers form a pure pipeline system, the latency for the last peer of the chain is $N$, being $N$ the number of peers. In a chain, the *diameter of the overlay* $D$ equals $N$. The ratio $D/R$ which measures 

2. Trees. Tree overlays place peers into a tree structure and impose that
peers must send so many copies of the stream (replication factor) as
the degree of the tree (usually $R=2$). Like chains, most tree overlays are driven by
push-based protocols aothough in this case, the latency is proportional to $D=\log_2(N)$ (notice, at the expense of sending each chunk twice than in the previous case). Therefore, the ratio 

3. Meshes. Mesh overlays are more flexible regarding their topology and $R$. However, because chunks can follow different paths, peers need to ask to their neighbors about the their availability. If this happens, we say that the overlay follows a *pull-based* protocol, which obviously, produce more transmission overhead that push-based ones. P2PSP is a push-based fully connected ($D=1$) $R=1$ mesh overlay.

![](http://slides.p2psp.org/2015-06-Barcelona/FIGs/full-mesh.svg)

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
