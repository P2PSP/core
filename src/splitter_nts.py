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
import time
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
        # {{{ The source port steps (smallest difference of the source ports
        # when connecting to different endpoints) of the peers in the team.
        # }}}
        self.port_steps = {}

        # {{{ The arriving peers. Key: ID.
        # Value: (serve_socket, peer_address,
        # source_port_to_splitter, source_port_to_monitor, arrive_time)
        # where source_port_to_splitter is the public source port towards the splitter
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
            # Also send the port step of the existing peer, in case
            # it is behind a sequentially allocating NAT
            message = self.ids[p] + struct.pack("4sHH", socket.inet_aton(p[ADDR]), \
                socket.htons(p[PORT]), self.port_steps[p])
            peer_serve_socket.sendall(message)

        # }}}

    def check_arriving_peer_time(self):
        # {{{ Remove peers that are waiting to be incorporated for too long

        now = time.time()
        peers_to_remove = []
        # Build list of arriving peers to remove
        for peer_id in self.arriving_peers:
            if now - self.arriving_peers[peer_id][4] > common.MAX_PEER_ARRIVING_TIME:
                peers_to_remove.append(peer_id)
        # Actually remove the peers
        for peer_id in peers_to_remove:
            print('NTS: Removed arriving peer %s due to timeout\n' % peer_id)
            # Close socket
            self.arriving_peers[peer_id][0].close()
            # Remove peer
            del self.arriving_peers[peer_id]

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
                                  new_peer[1], new_peer[1])
            return new_peer
        else:
            # Remove peers that are waiting to be incorporated for too long
            self.check_arriving_peer_time()
            self.arriving_peers[peer_id] = (serve_socket, new_peer[0], 0, 0, time.time())
            # Splitter will continue with incorporate_peer() as soon as the arriving
            # peer has sent UDP packets to splitter and monitor

        # }}}

    def incorporate_peer(self, peer_id, serve_socket, peer_address,
                         source_port_to_splitter, source_port_to_monitor):
        # {{{

        print("NTS: Incorporating the peer %s. Source ports: %s, %s"
            % (peer_id, source_port_to_splitter, source_port_to_monitor))

        if len(self.peer_list) != 0:
            self.send_the_list_of_peers_2(serve_socket)

        new_peer = (peer_address, source_port_to_splitter)
        port_diff = abs(source_port_to_monitor - source_port_to_splitter)

        if __debug__:
            print("NTS: Sending [send hello to %s]" % (new_peer,))
        # Send packets to all peers;
        for peer_number, peer in enumerate(self.peer_list):
            if peer_number == 0:
                # Send only the endpoint of the peer to the monitor,
                # as the arriving peer and the monitor already communicated
                message = peer_id + struct.pack("4sH", socket.inet_aton(peer_address), \
                    socket.htons(source_port_to_monitor))
            else:
                # Send all information necessary for port prediction to the existing peers
                message = peer_id + struct.pack("4sHHH", socket.inet_aton(peer_address), \
                    socket.htons(source_port_to_splitter), socket.htons(port_diff), \
                    socket.htons(peer_number))

            # Hopefully one of these packets arrives
            self.team_socket.sendto(message, peer)
            self.team_socket.sendto(message, peer)
            self.team_socket.sendto(message, peer)

        # Insert the peer into the list
        self.ids[new_peer] = peer_id
        self.port_steps[new_peer] = port_diff
        self.insert_peer(new_peer)
        serve_socket.close()

        # }}}

    def remove_peer(self, peer):
        # {{{

        Splitter_DBS.remove_peer(self, peer)

        try:
            del self.ids[peer]
            del self.port_steps[peer]
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
            elif len(message) == common.PEER_ID_LENGTH:
                # Packet is from the arriving peer itself
                peer_id = message
                print('NTS: Received hello (ID %s) from %s' % (peer_id, sender))
                # Send acknowledge
                self.team_socket.sendto(message, sender)
                if peer_id not in self.arriving_peers:
                    print('NTS: Peer ID %s is not an arriving peer' % peer_id)
                    continue

                peer_data = self.arriving_peers[peer_id]
                if peer_data[1] != sender[0]:
                    print('NTS: ID %s: peer address over TCP (%s) and UDP (%s) is different'
                        % (peer_id, peer_data[1], sender[0]))
                source_port_to_splitter = sender[1]
                peer_data = (peer_data[0], peer_data[1],
                    source_port_to_splitter, peer_data[3], peer_data[4])

                # Update peer information
                self.arriving_peers[peer_id] = peer_data

                if peer_data[2] != 0 and peer_data[3] != 0:
                    # Source ports are known, incorporate the peer
                    del self.arriving_peers[peer_id]
                    self.incorporate_peer(peer_id, *peer_data[:-1])
            elif len(self.peer_list) > 0 and sender == self.peer_list[0] and \
                len(message) == common.PEER_ID_LENGTH + struct.calcsize("H"):
                # Packet is from monitor
                peer_id = message[:common.PEER_ID_LENGTH]
                print('NTS: Received hello (ID %s) from %s' % (peer_id, sender))
                # Send acknowledge
                self.team_socket.sendto(message, sender)
                if peer_id not in self.arriving_peers:
                    print('NTS: Peer ID %s is not an arriving peer' % peer_id)
                    continue

                peer_data = self.arriving_peers[peer_id]
                source_port_to_monitor = socket.ntohs(struct.unpack("H",
                    message[common.PEER_ID_LENGTH:])[0])
                peer_data = (peer_data[0], peer_data[1], peer_data[2],
                    source_port_to_monitor, peer_data[4])

                # Update peer information
                self.arriving_peers[peer_id] = peer_data

                if peer_data[2] != 0 and peer_data[3] != 0:
                    # All source ports are known, incorporate the peer
                    del self.arriving_peers[peer_id]
                    self.incorporate_peer(peer_id, *peer_data[:-1])
            # }}}

        # }}}

    # }}}
