Message format
==============

After the initial TCP connection with the splitter, a peer communicates with
splitter, monitors and other peers over UDP messages. A NAT device can cause
different public endpoints of a host over TCP and UDP. Therefore, each peer
connecting to the splitter receives a unique ID. In the P2PSP software, this ID
has a fixed width and human readable characters, and consists of 7 uppercase
letters and/or decimal digits, allowing for a number of combinations similar to
a 32 bit integer variable.

Apart from video chunks with a length of 1026 bytes, there are only "hello"
messages occurring in the NAT Traversal Set of rules, used by new peers to
announce their presence. Each message received at splitter, monitors or peers
will be acknowledged by exactly the same message sent once back.

*Regular peers* send their own ID to monitors and other peers upon
incorporating. When the incorporation succeeds, the peer sends its ID together
with the character 'Y' to the splitter. When incorporation fails, the peer
creates a new socket and with that sends its ID and the character 'N' to
splitter and monitors, requesting a retry of incorporation.

*Monitors* only receive hello messages from a new peer, acknowledge them and
forward them to the splitter, appending the source port of the sending peer.

*The splitter* sends messages to inform incorporated or currently incorporating
peers of newly arriving peers. The message consists of the ID, IP address,
source port towards splitter and port step of the new peer, and the peer number
of the receiving peer. If the receiving peer is behind a NAT, the splitter also
appends the port of an extra socket it is listening to, to learn the currently
allocated source port of that peer.

As the most important host, the splitter does not store messages and wait for
acknowledge, but instead sends each message 3 times to ensure arrival of at
least one.

As each message type is uniquely identified by the type of sending and
receiving host (peer/monitor/splitter) and the number of bytes in addition to
the ID, currently no further message header is necessary. In future protocol
versions, a message header including a field for a message type ID might be
introduced, to allow different message types of the same length.
