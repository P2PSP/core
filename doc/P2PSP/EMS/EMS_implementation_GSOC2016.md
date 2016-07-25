Implementation of Endpoint Masquerading Set of Rules (EMS)
==========================================================
In modern computer networks, NAT (network address translation) routers and some security-motivated features found in them create problems for effective communication in a p2p protocol. EMS aims to solve the problem of communication among two or more peers found behind the same NAT router (in other words the same private router). This document details how this additional functionality was added to the existing p2psp codebase by extending NTS(NAT traversal set of rules) as a part of Google Summer of Code 2016.


## EMS in the P2PSP protocol

The solution prescribed to the EMS problem can be found in the p2psp protocol [description](http://www.ual.es/~vruiz/Investigacion/P2PSP/docs/main/WhitePaper/HTML/indexsu8.xht#x16-130004.8). The basic idea is to take advantage of 2 attributes of the splitter. 

1. a splitter holds a list of all the peers in a team 
2. a splitter is responsible for sending this list of peers to each new peer that joins a team

The solution is to have each joining peer send to the splitter its local endpoint (in its own LAN). The splitter will then know about both the private and public endpoint of each peer. When the list of peers is sent out to a new peer, the splitter will make sure that for peers found in the same LAN as the new peer (denoted by the fact that the 2 share the same public address), the private endpoint will be sent instead of the public one. In this way each new peer will always recognize its neighbor peers in the same LAN by their local endpoints which can be easily resolved by ARP.

## The EMS Peer
The EMS peer is completely identical to the NTS peer except for the addition of a message to the splitter sent when the peer is joining a team. This is achieved by overriding ConnectToTheSplitter method in the IMS (IP Multicast set of rules) layer. The EMS version of ConnectToTheSplitter simply calls the IMS method to join a splitter as usual. After the IMS method returns successfully and the peer makes a successful connection with the splitter, the peer gets the local endpoint from its socket connection to the splitter and sends this information to the splitter. The splitter will need to make sure to process this message. 

## The EMS Monitor 
No changes are made to the monitor compared to NTS, it simply inherits from the EMS peer like the NTS monitor does the NTS peer and has duplicates of the methods found in the NTS Monitor to preserve NAT traversal functionality

## The EMS Splitter
The EMS Splitter extends the NTS Splitter in 3 ways. First, add a map of public to private endpoints of all peers in the team. Second, receive the peer's local endpoint message when handling its arrival. Third, as each element of the peer list is sent to a new peer, use the map of public to private endpoints to ensure that the new peer will receive the private endpoints of neighboring peers that share its local area network (are behind the same NAT device). The extensions to the NTS splitter are designed to minimize code changes and interference with NTS logic.

### Map of Public to Private Endpoints
Instead of replacing the list of peers with a list of tuples, which would entail many code changes wherever a the list of peers is used previously. It was decided that a Map be used instead, in this way, the only change needed would be a lookup when peer identifiers are sent out to new peers connecting to the splitter. A protected member called peer_pairs_ was added to the EMS splitter using boost::unordered_map which mapped each public peer endpoint to its private peer endpoint. A existing hash function from a similar map used in the DBS layer to track lost chunks was reused here to produce a hash key based on each public endpoint. Since each peer has a different public endpoint, hash collisions are unlikely. Access and Removal time complexity should also be minimal.

### Handling Peer Arrival
The change in HandlePeerArrival which slightly extends the same method in NTS corresponds to receiving the peer's private endpoint message. This is done at the very beginning of the method to correspond to when the message is sent from the peer end.

### Sending List of Peers
In the NTS layer, the list of peers is sent out in 2 stages with 2 different methods with difference in logic due to the design of NAT traversal techniques. One such method concerns the sending of monitor peers, since it is assumed in p2psp protocol that monitor peers should not be behind NAT devices, this method (SendTheListofPeers) is untouched despite the monitor also sending its "private" endpoint as part the EMS monitor extends the EMS peer (which has the sending of private endpoint included by default when connecting to a splitter). The monitor's entry in the map of public to private peers is never used. 


The NTS method which is charged with sending the peers which are not monitors is the one extended as part of EMS. SendTheListofPeers2 breaks down the sending process into 2 further parts, first the peers in the process of being incorporated, and second the already incorporated peers. Here the design choice of using a map instead of a list of peers becomes beneficial. Instead of going into NTS to edit lots of code concerning incorporated/unincorporated peers we rely on the fact that the map tracks each peer to have ever made contact with the splitter. This allows the change to SendTheListofPeers2 to be quite simple. Every time a existing peer identification (incorporated or not) is about to be sent out to a new peer, the new peer's public endpoint is checked against the public endpoint of the peer being sent, if they match, the private endpoint is sent instead. Thus all incoming peers will identify their local neighbors by their private endpoints as described in the EMS portion of the P2PSP protocol document.





