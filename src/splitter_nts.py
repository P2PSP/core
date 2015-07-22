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

        # {{{ The arriving peers. Key: ID. Value: serve_socket.
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

        # For NTS, only send the monitor peer, as the other peers' endpoints
        # are sent together with their IDs when a Peer_NTS instance has been
        # created from the Peer_DBS instance

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

    def handle_a_peer_arrival(self, connection):
        # {{{

        # {{{ This method implements the NAT traversal algorithms of NTS of rules.
        # }}}

        serve_socket = connection[0]
        new_peer = connection[1]
        sys.stdout.write(Color.green)
        print(serve_socket.getsockname(), 'NTS: accepted connection from peer', \
              new_peer)
        sys.stdout.write(Color.none)
        self.send_configuration(serve_socket)
        self.send_the_list_of_peers(serve_socket)
        # Send the generated ID to peer
        peer_id = self.generate_id()
        print("NTS: sending ID %s to peer %s" % (peer_id, new_peer))
        serve_socket.sendall(peer_id)
        if len(self.peer_list) == 0:
            # Directly incorporate the monitor peer into the team
            self.incorporate_peer(serve_socket, new_peer)
            return new_peer
        else:
            self.arriving_peers[peer_id] = serve_socket
            # Splitter will continue with incorporate_peer() as soon as the arriving
            # peer has sent UDP packets to splitter and monitor

        # }}}

    def incorporate_peer(self, serve_socket, new_peer):
        # {{{

        #self.send_the_list_of_peers_2(serve_socket)

        if __debug__:
            print("NTS: sending [send hello to %s]" % (new_peer,))
            counter = 0
        message = struct.pack("4sH", socket.inet_aton(new_peer[0]), \
                              socket.htons(new_peer[1]))
        for peer in self.peer_list:
            self.team_socket.sendto(message, peer)
            if __debug__:
                print("NTS: [%5d]" % counter, peer)
                counter += 1

        # Insert the peer into the list
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
                # The longest possible message has length common.PEER_ID_LENGTH
                message, sender = self.team_socket.recvfrom(common.PEER_ID_LENGTH)
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
                peer_id = message
                print('NTS: received hello (ID %s) from %s' % (peer_id, sender))
                # Send acknowledge
                self.team_socket.sendto(peer_id, sender)
                # Incorporate the peer
                self.incorporate_peer(self.arriving_peers[peer_id], sender)
            # }}}

        # }}}

    # }}}
