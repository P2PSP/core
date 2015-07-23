# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports
import common
import random
import string
import sys
import struct
import socket
from splitter_dbs import Splitter_DBS, ADDR, PORT
from color import Color
# }}}

# NTS: NAT Traversal Set of rules
class Splitter_NTS(Splitter_DBS):
    # {{{

    def __init__(self):
        # {{{

        Splitter_DBS.__init__(self)
        sys.stdout.write(Color.yellow)
        print("Using NTS")
        sys.stdout.write(Color.none)

        # {{{ The IDs of the peers in the team.
        # }}}
        self.ids = {}

        # {{{ The arriving peers. Key: ID.
        # Value: (serve_socket, peer_address, source_port_local,
        # source_port_to_splitter, source_port_to_monitor)
        # where source_port_local is the local source port towards the NAT,
        # source_port_to_splitter is the public source port towards the splitter,
        # and source_port_to_monitor is the public source port towards the monitor.
        # }}}
        self.arriving_peers = {}

        # }}}

    def say_goodbye(self, node, sock):
        # {{{

        sock.sendto(b'G', node)

        # }}}

    def generate_id(self):
        # {{{ Generate a random ID for a newly arriving peer

        return ''.join(random.choice(string.ascii_uppercase + string.digits)
            for _ in range(common.PEER_ID_LENGTH))

        # }}}

    def send_the_list_of_peers(self, peer_serve_socket):
        # {{{

        # For NTS, send only the monitor peer, as the other peers' endpoints
        # are sent together with their IDs when a Peer_NTS instance has been
        # created from the Peer_DBS instance, in send_the_list_of_peers_2()

        if len(self.peer_list) == 0:
            print("NTS: Sending an empty list of peers")
            message = struct.pack("H", socket.htons(0))
            peer_serve_socket.sendall(message)
        else:
            print("NTS: Sending the monitor as the list of peers")
            # Send a peer list size of 1
            message = struct.pack("H", socket.htons(1))
            peer_serve_socket.sendall(message)
            # Send the monitor endpoint
            message = struct.pack("4sH", socket.inet_aton(self.peer_list[0][ADDR]), \
                                  socket.htons(self.peer_list[0][PORT]))
            peer_serve_socket.sendall(message)

        # }}}

    def send_the_list_of_peers_2(self, peer_serve_socket):
        # {{{

        # Send all peers except the monitor peer with their peer ID
        if __debug__:
            print("DBS: Sending the list of peers except the monitor (%d peers)",
                  len(self.peer_list)-1)
        message = struct.pack("H", socket.htons(len(self.peer_list)-1))
        peer_serve_socket.sendall(message)

        for p in self.peer_list[1:]:
            message = self.ids[p] + struct.pack("4sH", socket.inet_aton(p[ADDR]), \
                                                socket.htons(p[PORT]))
            peer_serve_socket.sendall(message)

        # }}}

    def handle_a_peer_arrival(self, connection):
        # {{{

        # {{{ This method implements the NAT traversal algorithms of NTS of rules.
        # }}}

        serve_socket = connection[0]
        new_peer = connection[1]
        sys.stdout.write(Color.green)
        print('NTS: Accepted connection from peer %s' % (new_peer,))
        sys.stdout.write(Color.none)
        self.send_configuration(serve_socket)
        self.send_the_list_of_peers(serve_socket)
        # Send the generated ID to peer
        peer_id = self.generate_id()
        print("NTS: Sending ID %s to peer %s" % (peer_id, new_peer))
        serve_socket.sendall(peer_id)
        if len(self.peer_list) == 0:
            # Directly incorporate the monitor peer into the team.
            # The source ports are all set to the same, as the monitor peer
            # should be publicly accessible
            self.incorporate_peer(peer_id, serve_socket, new_peer[0],
                                  new_peer[1], new_peer[1], new_peer[1])
            return new_peer
        else:
            self.arriving_peers[peer_id] = (serve_socket, new_peer[0], 0, 0, 0)
            # Splitter will continue with incorporate_peer() as soon as the arriving
            # peer has sent UDP packets to splitter and monitor

        # }}}

    def incorporate_peer(self, peer_id, serve_socket, peer_address, source_port_local,
                         source_port_to_splitter, source_port_to_monitor):
        # {{{

        print("NTS: Incorporating the peer %s. Source ports: %s, %s, %s"
            % (peer_id, source_port_local, source_port_to_splitter, source_port_to_monitor))

        if len(self.peer_list) != 0:
            self.send_the_list_of_peers_2(serve_socket)

        # This has to be adapted with port prediction
        new_peer = (peer_address, source_port_to_splitter)
        if __debug__:
            print("NTS: Sending [send hello to %s]" % (new_peer,))
        message = peer_id + struct.pack("4sH", socket.inet_aton(new_peer[0]), \
                                        socket.htons(new_peer[1]))
        # Send the packet to all peers except the monitor peer
        for peer in self.peer_list[1:]:
            # Hopefully this packet arrives
            self.team_socket.sendto(message, peer)
            self.team_socket.sendto(message, peer)
            self.team_socket.sendto(message, peer)

        # Insert the peer into the list
        self.ids[new_peer] = peer_id
        self.insert_peer(new_peer)
        serve_socket.close()

        # }}}

    def remove_peer(self, peer):
        # {{{

        Splitter_DBS.remove_peer(self, peer)

        try:
            del self.ids[peer]
        except KeyError:
            pass

        # }}}

    def moderate_the_team(self):
        # {{{

        while self.alive:
            # {{{

            try:
                # The longest possible message has length
                # common.PEER_ID_LENGTH + struct.calcsize("H")
                message, sender = self.team_socket.recvfrom(
                    common.PEER_ID_LENGTH + struct.calcsize("H"))
            except:
                print("NTS: Unexpected error:", sys.exc_info()[0])
                continue

            if len(message) == 2:

                # {{{ The peer complains about a lost chunk.

                # In this situation, the splitter counts the number of
                # complains. If this number exceeds a threshold, the
                # unsupportive peer is expelled from the
                # team.

                lost_chunk_number = self.get_lost_chunk_number(message)
                self.process_lost_chunk(lost_chunk_number, sender)

                # }}}

            elif message == 'G': # 'G'oodbye
                # {{{ The peer wants to leave the team.
                self.process_goodbye(sender)
                # }}}
            elif len(message) == common.PEER_ID_LENGTH + struct.calcsize("H"):
                peer_id = message[:common.PEER_ID_LENGTH]
                print('NTS: Received hello (ID %s) from %s' % (peer_id, sender))
                # Send acknowledge
                self.team_socket.sendto(message, sender)
                if peer_id not in self.arriving_peers:
                    print('NTS: Peer ID %s is unknown' % peer_id)
                    continue

                peer_data = self.arriving_peers[peer_id]
                reported_source_port = socket.ntohs(struct.unpack("H",
                    message[common.PEER_ID_LENGTH:])[0])
                if sender[ADDR] == self.peer_list[0][ADDR]:
                    # Packet is from monitor
                    source_port_to_monitor = reported_source_port
                    peer_data = (peer_data[0], peer_data[1], peer_data[2],
                        peer_data[3], source_port_to_monitor)
                else:
                    # Packet is from the arriving peer itself
                    if peer_data[1] != sender[0]:
                        print('NTS: ID %s: peer address over TCP (%s) and UDP (%s) is different'
                            % (peer_id, peer_data[1], sender[0]))
                    source_port_local = reported_source_port
                    source_port_to_splitter = sender[1]
                    peer_data = (peer_data[0], peer_data[1], source_port_local, source_port_to_splitter, peer_data[4])

                # Update peer information
                self.arriving_peers[peer_id] = peer_data

                if peer_data[2] != 0 and peer_data[3] != 0 and peer_data[4] != 0:
                    # All source ports are known, incorporate the peer
                    del self.arriving_peers[peer_id]
                    self.incorporate_peer(peer_id, *peer_data)
            # }}}

        # }}}

    # }}}
