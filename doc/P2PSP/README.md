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

P2PSP characteristics
---------------------

1. P2PSP is not aware of the broadcasted content, the bit-rate, the format, etc.
2. P2PSP has a modular architecture. The number of modules used depends on the requirements of the system to be deployed.
3. P2PSP emulates the behaviour of IP multicast. If this is available, this facility is used.
4. Due to usually lost chunks are spreaded along the time, P2PSP facilitates the use of error concealment techniques.

Data partitioning
-----------------

P2PSP splits the media stream into *chunks*. At this moment (the following is something that could be change in the future in order to achieve that a chunk transport a unit of code-stream), all chunks have the same size. Chunks are transmitted over [UDP](https://en.wikipedia.org/wiki/User_Datagram_Protocol). A small chunk minimizes the average latency of the transmission but also increments the [overhead](https://en.wikipedia.org/wiki/Protocol_overhead).

Entities
--------

A P2PSP overlay network is composed the entities (in general, nodes of the overlay).

1. A source which produces the stream. Typically, it is a streaming
  HTTP server using the HTTP protocol such as [Icecast](http://icecast.org/). The
  source controls the transmission bit-rate in the P2PSP network and
  in general can serve to several clients.

2. Players request and consume (decode and play) the stream.

3. Splitters. This entity receives the stream from a
  source, splits it into chunks and sends the chunks
  to peers. A splitter feeds a team (of peers). Teams can be interconnected if peers works as sources.

4. Peers that receive chunks from the splitter and from
  other peers, ensembles the stream (usuatlly using buffering) and sends it to a player.

Sets or Rules
-------------

The protocol is organized into layers, each of them implementing a different set of rules (SoR). Each
layer solves a specific problem.

1. [IMS (Ip Multicast Set of rules)](IMS/README.md)
2. [DBS (Data Broadcasting Set of rules)](DBS/README.md)
3. [LRS (Lost Recovery Set of rules)](LRS/README.md)
4. [ACS (Adaptive Chunk-rate Set of rules)](ACS/README.md)
5. [NTS (Nat Traversal Set of rules)](NTS/README.md)
7. [EMS (End-point Masquerading Set of rules)](EMS/README.md)
8. [CIS (Content Integrity Set of rules)](CIS/README.md) 
9. [DPS (Data Privacy Set of rules)](DPS/README.md) 
10. [MCS (Multi-Channel Set of rules)](MCS/README.md)
11. [RMS (Reliable Mode Set of rules)](RMS/README.md)
12. [ERS (Error Resilience Set or rules)](ERS/README.md)
13. [TCS (Team Clustering Set of rules)](TCS/README.md)
