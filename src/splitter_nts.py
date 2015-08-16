# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports
import common
from fractions import gcd
import random
import string
import sys
import struct
import socket
import threading
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

        # {{{ The peers that are being incorporated, have closed their TCP
        # connection to splitter and try to connect to all existing peers.
        # They will be removed from the team if taking too long to connect to peers.
        # key: peer_id; value: (peer, incorporation_time, source_port_to_splitter,
        # source_port_to_monitor, serve_socket).
        # The source port values are set when the peer retries incorporation.
        # }}}
        self.incorporating_peers = {}

        # The thread regularly checks if peers are waiting to be incorporated
        # for too long and removes them after a timeout
        threading.Thread(target=self.check_timeout_thread).start()

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

    def send_the_list_of_peers_2(self, peer_serve_socket, peer):
        # {{{

        # Send all peers except the monitor peer with their peer ID
        number_of_other_peers = len(self.peer_list)-1
        if peer in self.peer_list:
            number_of_other_peers -= 1
        if __debug__:
            print("DBS: Sending the list of peers except the monitor (%d peers)",
                  number_of_other_peers)
        message = struct.pack("H", socket.htons(number_of_other_peers))
        peer_serve_socket.sendall(message)

        for p in self.peer_list[1:]:
            if p == peer: # Do not send its endpoint to the peer itself
                continue
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
            print('NTS: Removed arriving peer %s due to timeout' % peer_id)
            # Close socket
            self.arriving_peers[peer_id][0].close()
            # Remove peer
            del self.arriving_peers[peer_id]

        # }}}

    def check_incorporating_peer_time(self):
        # {{{ Remove peers that are connecting to the existing peers too long

        now = time.time()
        peers_to_remove = []
        # Build list of incorporating peers to remove
        for peer_id in self.incorporating_peers:
            if now - self.incorporating_peers[peer_id][1] \
                > common.MAX_TOTAL_INCORPORATION_TIME:
                peers_to_remove.append(peer_id)
        # Actually remove the peers
        for peer_id in peers_to_remove:
            print('NTS: Removed incorporating peer %s due to timeout' % peer_id)
            # Close TCP socket
            self.incorporating_peers[peer_id][4].close()
            # Remove peer
            del self.incorporating_peers[peer_id]

        # }}}

    def check_timeout_thread(self):
        # {{{

        while self.alive:
            time.sleep(common.MAX_PEER_ARRIVING_TIME)
            # Remove peers that are waiting to be incorporated for too long
            self.check_arriving_peer_time()
            self.check_incorporating_peer_time()

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
            self.ids[new_peer] = peer_id
            self.port_steps[new_peer] = 0
            self.insert_peer(new_peer)
            serve_socket.close()
            return new_peer
        else:
            self.arriving_peers[peer_id] = (serve_socket, new_peer[0], 0, 0, time.time())
            # Splitter will continue with incorporate_peer() as soon as the arriving
            # peer has sent UDP packets to splitter and monitor

        # }}}

    def incorporate_peer(self, peer_id):
        # {{{

        serve_socket, peer_address, source_port_to_splitter, \
            source_port_to_monitor, arrive_time = self.arriving_peers[peer_id]

        print("NTS: Incorporating the peer %s. Source ports: %s, %s"
            % (peer_id, source_port_to_splitter, source_port_to_monitor))

        new_peer = (peer_address, source_port_to_splitter)
        if len(self.peer_list) != 0:
            try:
                self.send_the_list_of_peers_2(serve_socket, new_peer)
            except Exception as e:
                print("NTS: %s" % e)

        port_diff = abs(source_port_to_monitor - source_port_to_splitter)

        self.send_new_peer(peer_id, new_peer, port_diff, source_port_to_monitor)

        # Insert the peer into the list
        self.ids[new_peer] = peer_id
        self.port_steps[new_peer] = port_diff
        self.insert_peer(new_peer)
        # The peer is in the team, but is not connected to all peers yet,
        # so add to the list
        self.incorporating_peers[peer_id] = (new_peer, time.time(), 0, 0, serve_socket)

        del self.arriving_peers[peer_id]

        # }}}

    def send_new_peer(self, peer_id, new_peer, port_step, source_port_to_monitor):
        # {{{

        if __debug__:
            print("NTS: Sending [send hello to %s]" % (new_peer,))
        # Send packets to all peers;
        for peer_number, peer in enumerate(self.peer_list):
            if peer == new_peer: # Do not send its endpoint to the peer itself
                continue
            if peer_number == 0:
                # Send only the endpoint of the peer to the monitor,
                # as the arriving peer and the monitor already communicated
                message = peer_id + struct.pack("4sH", socket.inet_aton(new_peer[0]), \
                    socket.htons(source_port_to_monitor))
            else:
                # Send all information necessary for port prediction to the existing peers
                message = peer_id + struct.pack("4sHHH", socket.inet_aton(new_peer[0]), \
                    socket.htons(new_peer[1]), socket.htons(port_step), \
                    socket.htons(peer_number))

            # Hopefully one of these packets arrives
            self.team_socket.sendto(message, peer)
            self.team_socket.sendto(message, peer)
            self.team_socket.sendto(message, peer)

        # }}}

    def update_peer(self, peer, new_peer):
        # {{{

        # Put the updated peer to the end of the list, as it is newly connecting
        self.peer_list.remove(peer)
        self.peer_list.append(new_peer)

        self.ids[new_peer] = self.ids.pop(peer)
        self.port_steps[new_peer] = self.port_steps.pop(peer)
        self.losses[new_peer] = self.losses.pop(peer)

        # }}}

    def retry_to_incorporate_peer(self, peer_id):
        # {{{

        # Update source port information
        peer, start_time, source_port_to_splitter, source_port_to_monitor, \
            serve_socket = self.incorporating_peers[peer_id]
        self.update_port_step(peer, source_port_to_splitter)
        self.update_port_step(peer, source_port_to_monitor)
        # Update peer lists
        new_peer = (peer[0], source_port_to_splitter)
        self.update_peer(peer, new_peer)
        self.incorporating_peers[peer_id] = (new_peer, start_time, 0, 0, serve_socket)

        # Send the updated endpoint to the existing peers
        self.send_new_peer(peer_id, new_peer, self.port_steps[new_peer],
            source_port_to_monitor)

        # Send all peers to the retrying peer
        try:
            self.send_the_list_of_peers_2(serve_socket, new_peer)
        except Exception as e:
            print("NTS: %s" % e)

        # }}}

    def update_port_step(self, peer, source_port):
        # {{{

        # Skip check if measured port step is 0
        if self.port_steps[peer] == 0:
            return
        # Update source port information
        port_diff = abs(peer[1] - source_port)
        previous_port_step = self.port_steps[peer]
        self.port_steps[peer] = gcd(previous_port_step, port_diff)
        if self.port_steps[peer] != previous_port_step:
            print('NTS: Updated port step of peer %s from %d to %d' %
                (peer, previous_port_step, self.port_steps[peer]))

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
                # common.PEER_ID_LENGTH+1 + struct.calcsize("H")
                message, sender = self.team_socket.recvfrom(
                    common.PEER_ID_LENGTH+1 + struct.calcsize("H"))
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
                # Update peer information
                self.arriving_peers[peer_id] = (peer_data[0], peer_data[1],
                    source_port_to_splitter, peer_data[3], peer_data[4])

                if source_port_to_splitter != 0 and peer_data[3] != 0:
                    # Source ports are known, incorporate the peer
                    self.incorporate_peer(peer_id)

            elif len(self.peer_list) > 0 and sender == self.peer_list[0] and \
                len(message) == common.PEER_ID_LENGTH + struct.calcsize("H"):
                # Packet is from monitor
                peer_id = message[:common.PEER_ID_LENGTH]
                print('NTS: Received forwarded hello (ID %s) from %s' % (peer_id, sender))
                # Send acknowledge
                self.team_socket.sendto(message, sender)
                if peer_id not in self.arriving_peers:
                    print('NTS: Peer ID %s is not an arriving peer' % peer_id)
                    continue

                peer_data = self.arriving_peers[peer_id]
                source_port_to_monitor = socket.ntohs(struct.unpack("H",
                    message[common.PEER_ID_LENGTH:])[0])
                # Update peer information
                self.arriving_peers[peer_id] = (peer_data[0], peer_data[1],
                    peer_data[2], source_port_to_monitor, peer_data[4])

                if peer_data[2] != 0 and source_port_to_monitor != 0:
                    # All source ports are known, incorporate the peer
                    self.incorporate_peer(peer_id)

            elif len(message) == common.PEER_ID_LENGTH + struct.calcsize("H"):
                # Received source port of a peer from another peer
                peer_id = message[:common.PEER_ID_LENGTH]
                print('NTS: Received source port of peer %s from %s' % (peer_id, sender))
                # Send acknowledge
                self.team_socket.sendto(message, sender)

                peer = None
                for peer_data in self.ids.iteritems():
                    if peer_id == peer_data[1]:
                        peer = peer_data[0]
                        break
                if peer == None:
                    print('NTS: Peer ID %s unknown' % peer_id)
                    continue

                source_port = socket.ntohs(struct.unpack("H",
                    message[common.PEER_ID_LENGTH:])[0])

                # Update source port information
                self.update_port_step(peer, source_port)

            elif len(message) == common.PEER_ID_LENGTH + 1:
                # A peer succeeded or failed to be incorporated into the team
                peer_id = message[:common.PEER_ID_LENGTH]
                # Send acknowledge
                self.team_socket.sendto(message, sender)

                if peer_id not in self.incorporating_peers:
                    print('NTS: Unknown peer %s' % peer_id)
                    continue
                # Check sender address
                if sender[0] != self.incorporating_peers[peer_id][0][0]:
                    print('NTS: Peer %s switched from %s to %s, ignoring request' \
                        % (peer_id, sender[0], self.incorporating_peers[peer_id][0][0]))
                    continue

                if message[-1] == 'Y':
                    print('NTS: Peer %s was successfully incorporated' % peer_id)
                    # Close TCP socket
                    self.incorporating_peers[peer_id][4].close()
                    del self.incorporating_peers[peer_id]
                else:
                    if sender[1] == self.incorporating_peers[peer_id][0][1]:
                        print('NTS: Peer %s retries incorporation from same port, ignoring' % peer_id)
                        continue
                    print('NTS: Peer %s retries incorporation from %s' % (peer_id, sender))
                    peer_data = self.incorporating_peers[peer_id]
                    source_port_to_splitter = sender[1]
                    # Update peer information
                    self.incorporating_peers[peer_id] = (peer_data[0], peer_data[1],
                        source_port_to_splitter, peer_data[3], peer_data[4])

                    if source_port_to_splitter != 0 and peer_data[3] != 0:
                        # All source ports are known, incorporate the peer
                        self.retry_to_incorporate_peer(peer_id)

            elif len(self.peer_list) > 0 and sender == self.peer_list[0] and \
                len(message) == common.PEER_ID_LENGTH+1 + struct.calcsize("H"):
                # Packet is from monitor
                peer_id = message[:common.PEER_ID_LENGTH]
                print('NTS: Received forwarded retry hello (ID %s)' % (peer_id,))
                # Send acknowledge
                self.team_socket.sendto(message, sender)
                if peer_id not in self.incorporating_peers:
                    print('NTS: Peer ID %s is not an incorporating peer' % peer_id)
                    continue

                peer_data = self.incorporating_peers[peer_id]
                source_port_to_monitor = socket.ntohs(struct.unpack("H",
                    message[common.PEER_ID_LENGTH+1:])[0])
                # Update peer information
                self.incorporating_peers[peer_id] = (peer_data[0], peer_data[1],
                    peer_data[2], source_port_to_monitor, peer_data[4])

                if peer_data[2] != 0 and source_port_to_monitor != 0:
                    # All source ports are known, incorporate the peer
                    self.retry_to_incorporate_peer(peer_id)

            else:
                print('NTS: Ignoring packet of length %d from %s' \
                    % (len(message), sender))

            # }}}

        # }}}

    # }}}
