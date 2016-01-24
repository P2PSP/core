"""
@package core
peer_dbs splitter_nts
"""

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team
# http://www.p2psp.org

# NTS: NAT Traversal Set of rules

# {{{ Imports

from fractions import gcd
import queue
import random
import string
import sys
import struct
import socket
import threading
import time

from core.common import Common
from core.splitter_dbs import Splitter_DBS, ADDR, PORT
from core.color import Color
from core._print_ import _print_

# }}}

def _p_(*args, **kwargs):
    """Colorize the output."""
    if __debug__:
        sys.stdout.write(Common.NTS_COLOR)
        _print_("NTS:", *args)
        sys.stdout.write(Color.none)

class Splitter_NTS(Splitter_DBS):
    # {{{

    def __init__(self, splitter):
        # {{{

        #Splitter_DBS.__init__(self)    # Ojo, comentar
        #sys.stdout.write(Color.yellow)
        #print("Using NTS")
        #sys.stdout.write(Color.none)

        # {{{ The IDs of the peers in the team.
        # }}}
        self.ids = {}
        # {{{ The source port steps (smallest difference of the source ports
        # when connecting to different endpoints) of the peers in the team.
        # }}}
        self.port_steps = {}

        # {{{ The last known allocated source port for each peer in the team.
        # }}}
        self.last_source_port = {}

        # {{{ The arriving peers. Key: ID.
        # Value: (serve_socket, peer_address,
        # source_port_to_splitter, source_ports_to_monitors, arrive_time)
        # where source_port_to_splitter is the public source port to splitter
        # and source_ports_to_monitors are the source ports towards monitors.
        # }}}
        self.arriving_peers = {}

        # {{{ The peers that are being incorporated, have closed their TCP
        # connection to splitter and try to connect to all existing peers.
        # They will be removed from team if taking too long to connect to peers.
        # key: peer_id; value: (peer, incorporation_time,
        # source_port_to_splitter, source_ports_to_monitors, serve_socket).
        # The source port values are set when the peer retries incorporation.
        # }}}
        self.incorporating_peers = {}

        # The thread regularly checks if peers are waiting to be incorporated
        # for too long and removes them after a timeout
        threading.Thread(target=self.check_timeout_thread).start()

        # This socket is closed and created again when a new peer arrives,
        # and all incorporated peers with port_step != 0 send a message to this
        # socket to determine the currently allocated source port
        self.extra_socket = None
        # The thread listens to self.extra_socket and reports source ports
        threading.Thread(target=self.listen_extra_socket_thread).start()

        # This message queue stores tuples (message, sender) that will be sent
        # in a dedicated thread instead of the main thread, with a delay between
        # each message to avoid network congestion.
        self.message_queue = queue.Queue()
        threading.Thread(target=self.send_message_thread).start()
        # An event that is set for each chunk received by the source
        self.chunk_received_event = threading.Event()

        self.magic_flags |= Common.NTS

        # }}}

    def receive_chunk(self):
        # {{{

        chunk = Splitter_DBS.receive_chunk(self)
        self.chunk_received_event.set()
        return chunk

        # }}}

    def send_message_thread(self):
        # {{{

        while self.alive:
            # Wait for an enqueued message
            message, peer = self.message_queue.get()
            # Send the message
            self.team_socket.sendto(message, peer)
            # Wait for a chunk from source to avoid network congestion
            self.chunk_received_event.wait()
            self.chunk_received_event.clear()
            self.message_queue.task_done()

        # }}}

    def say_goodbye(self, node, sock):
        # {{{

        sock.sendto(b'G', node)

        # }}}

    def generate_id(self):
        # {{{ Generate a random ID for a newly arriving peer
        # This has about the same number of combinations as a 32 bit integer

        return ''.join(random.choice(string.ascii_uppercase + string.digits)
                       for _ in range(Common.PEER_ID_LENGTH))

        # }}}

    def send_the_list_of_peers(self, peer_serve_socket):
        # {{{

        # For NTS, send only the monitor peer, as the other peers' endpoints
        # are sent together with their IDs when a Peer_NTS instance has been
        # created from the Peer_DBS instance, in send_the_list_of_peers_2()

        if __debug__:
            _p_("Sending the monitors as the list of peers")
        # Send the number of monitors
        message = struct.pack("H", socket.htons(self.MONITOR_NUMBER))
        peer_serve_socket.sendall(message)
        # Send a peer list size equal to the number of monitor peers
        message = struct.pack("H", socket.htons(min(self.MONITOR_NUMBER,
                                                    len(self.peer_list))))
        peer_serve_socket.sendall(message)
        # Send the monitor endpoints
        for peer in self.peer_list[:self.MONITOR_NUMBER]:
            message = struct.pack("4sH", socket.inet_aton(peer[ADDR]), \
                                  socket.htons(peer[PORT]))
            peer_serve_socket.sendall(message)

        # }}}

    def send_the_list_of_peers_2(self, peer_serve_socket, peer):
        # {{{

        # Send all peers except the monitor peers with their peer ID
        # plus all peers currently being incorporated
        number_of_other_peers = len(self.peer_list) - self.MONITOR_NUMBER \
            + len(self.incorporating_peers)
        if peer in self.ids:
            # Then peer is also in self.incorporating_peers
            # Do not send the peer endpoint to itself
            number_of_other_peers = max(0, number_of_other_peers - 1)
        if __debug__:
            _p_("Sending the list of peers except monitors (%d peers)" \
                % number_of_other_peers)
        message = struct.pack("H", socket.htons(number_of_other_peers))
        peer_serve_socket.sendall(message)

        for p in self.peer_list[self.MONITOR_NUMBER:]:
            # Also send the port step of the existing peer, in case
            # it is behind a sequentially allocating NAT
            message = self.ids[p].encode() + struct.pack( \
                    "4sHH", socket.inet_aton(p[ADDR]),
                    socket.htons(self.last_source_port[p]),
                    socket.htons(self.port_steps[p]))
            peer_serve_socket.sendall(message)
        # Send the peers currently being incorporated
        for peer_id in self.incorporating_peers:
            # Do not send the peer endpoint to itself
            if peer in self.ids and peer_id == self.ids[peer]:
                continue
            if __debug__:
                _p_("Sending peer %s to %s" % (peer_id, peer))
            p = self.incorporating_peers[peer_id][0]
            message = peer_id.encode() + struct.pack( \
                "4sHH", socket.inet_aton(p[ADDR]),
                socket.htons(self.last_source_port[p]),
                socket.htons(self.port_steps[p]))
            peer_serve_socket.sendall(message)

        # }}}

    def check_arriving_peer_time(self):
        # {{{ Remove peers that are waiting to be incorporated too long

        now = time.time()
        peers_to_remove = []
        # Build list of arriving peers to remove
        for peer_id in self.arriving_peers:
            if now - self.arriving_peers[peer_id][4] \
            > Common.MAX_PEER_ARRIVING_TIME:
                peers_to_remove.append(peer_id)
        # Actually remove the peers
        for peer_id in peers_to_remove:
            _p_('Removed arriving peer %s due to timeout' % peer_id)
            # Close socket
            self.arriving_peers[peer_id][0].close()
            # Remove peer
            peer = self.arriving_peers[peer_id][1:3]
            del self.last_source_port[peer]
            del self.arriving_peers[peer_id]

        # }}}

    def check_incorporating_peer_time(self):
        # {{{ Remove peers that try to connect to the existing peers too long

        now = time.time()
        peers_to_remove = []
        # Build list of incorporating peers to remove
        for peer_id in self.incorporating_peers:
            if now - self.incorporating_peers[peer_id][1] \
                > Common.MAX_TOTAL_INCORPORATION_TIME:
                peers_to_remove.append(peer_id)
        # Actually remove the peers
        for peer_id in peers_to_remove:
            _p_('Removed incorporating peer %s due to timeout' % peer_id)
            # Close TCP socket
            self.incorporating_peers[peer_id][4].close()
            # Remove peer
            peer = self.incorporating_peers[peer_id][0]
            del self.ids[peer]
            del self.port_steps[peer]
            del self.last_source_port[peer]
            del self.incorporating_peers[peer_id]

        # }}}

    def check_timeout_thread(self):
        # {{{

        while self.alive:
            time.sleep(Common.MAX_PEER_ARRIVING_TIME)
            # Check timeouts
            self.check_arriving_peer_time()
            self.check_incorporating_peer_time()

        # }}}

    def listen_extra_socket_thread(self):
        # {{{

        # The thread listens to self.extra_socket to determine the currently
        # allocated source port of incorporated peers behind SYMSP NATs

        # Wait until socket is created
        while self.alive and self.extra_socket == None:
            time.sleep(1)

        while self.alive:
            # {{{

            # Receive messages
            try:
                message, sender = \
                    self.extra_socket.recvfrom(Common.PEER_ID_LENGTH)
            except socket.timeout:
                # Ignore timeout
                continue
            except:
                _p_("Unexpected error:", sys.exc_info()[0])
                continue

            if len(message) == Common.PEER_ID_LENGTH:
                # Send acknowledge
                self.extra_socket.sendto(message, sender)

                peer_id = message.decode()

                peer = None
                for peer_data in self.ids.items():
                    if peer_id == peer_data[1]:
                        peer = peer_data[0]
                        break
                if peer == None:
                    _p_('Peer ID %s unknown' % peer_id)
                    continue
                # Check sender address
                if sender[0] != peer[0]:
                    _p_('Peer %s switched from %s to %s, ignoring' % (peer_id, peer[0], sender[0]))
                    continue
                # Update source port information
                _p_('Received current source port %d of peer %s\n' % (sender[1], peer_id))
                self.update_port_step(peer, sender[1])
            else:
                _p_('Ignoring packet of length %d from %s' % (len(message), sender))


            # }}}

        # }}}

    def handle_a_peer_arrival(self, connection):
        # {{{

        # {{{ This method implements the NAT traversal algorithms.
        # }}}

        serve_socket = connection[0]
        new_peer = connection[1]
        sys.stdout.write(Color.green)
        _p_('Accepted connection from peer %s' % (new_peer,))
        sys.stdout.write(Color.none)
        self.send_configuration(serve_socket)
        self.send_the_list_of_peers(serve_socket)
        # Send the generated ID to peer
        peer_id = self.generate_id()
        _p_("Sending ID %s to peer %s" % (peer_id, new_peer))
        #message = struct.pack(str(Common.PEER_ID_LENGTH) + "s", bytes(peer_id).encode())
        serve_socket.sendall(peer_id.encode())
        if len(self.peer_list) < self.MONITOR_NUMBER:
            # Directly incorporate the monitor peer into the team.
            # The source ports are all set to the same, as the monitor peers
            # should be publicly accessible
            self.ids[new_peer] = peer_id
            self.port_steps[new_peer] = 0
            self.last_source_port[new_peer] = new_peer[1]
            self.send_new_peer(peer_id, new_peer,
                               [new_peer[1]]*self.MONITOR_NUMBER)
            self.insert_peer(new_peer)
            serve_socket.close()
            return new_peer
        else:
            self.arriving_peers[peer_id] = (serve_socket, new_peer[0], 0, \
                [0]*self.MONITOR_NUMBER, time.time())
            # Splitter will continue with incorporate_peer() as soon as the
            # arriving peer has sent UDP packets to splitter and monitor

        # }}}

    def incorporate_peer(self, peer_id):
        # {{{

        serve_socket, peer_address, source_port_to_splitter, \
            source_ports_to_monitors, _ = self.arriving_peers[peer_id]

        _p_("Incorporating the peer %s. Source ports: %s, %s"
              % (peer_id, source_port_to_splitter, source_ports_to_monitors))

        new_peer = (peer_address, source_port_to_splitter)
        if len(self.peer_list) >= self.MONITOR_NUMBER:
            try:
                # Send the endpoints of the incorporated peers to the new peer
                self.send_the_list_of_peers_2(serve_socket, new_peer)
            except Exception as e:
                _p_("%s" % e)

        self.port_steps[new_peer] = None
        for source_port_to_monitor in source_ports_to_monitors:
            self.update_port_step(new_peer, source_port_to_monitor)

        # Send the new peer endpoint to the incorporated peers
        self.send_new_peer(peer_id, new_peer, source_ports_to_monitors)

        # Insert the peer into the list
        self.ids[new_peer] = peer_id
        # The peer is in the team, but is not connected to all peers yet,
        # so add to the list
        self.incorporating_peers[peer_id] = (new_peer, time.time(), 0, \
            [0]*self.MONITOR_NUMBER, serve_socket)

        del self.arriving_peers[peer_id]

        # }}}

    def send_new_peer(self, peer_id, new_peer, source_ports_to_monitors):
        # {{{

        # Recreate self.extra_socket, listening to a random port
        if self.extra_socket != None:
            self.extra_socket.close()
        self.extra_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.extra_socket.bind(('', 0))
        self.extra_socket.settimeout(1) # To not block the thread forever
        extra_listen_port = self.extra_socket.getsockname()[1]
        if __debug__:
            _p_("Listening to the extra port %d" % extra_listen_port)
            _p_("Sending [send hello to %s]" % (new_peer,))
        # The peers start port prediction at the minimum known source port,
        # counting up using their peer_number
        min_known_source_port = min(source_ports_to_monitors + [new_peer[1]])
        # Send packets to all peers;
        for peer_number, peer in enumerate(self.peer_list):
            if peer_number < self.MONITOR_NUMBER:
                # Send only the endpoint of the peer to the monitor,
                # as the arriving peer and the monitor already communicated
                message = peer_id.encode() + struct.pack( \
                    "4sH", socket.inet_aton(new_peer[0]),
                    socket.htons(source_ports_to_monitors[peer_number]))
            else:
                # Send all information necessary for port prediction to the
                # existing peers
                if self.port_steps[peer] == 0:
                    message = peer_id.encode() + struct.pack(\
                        "4sHHH", socket.inet_aton(new_peer[0]),
                        socket.htons(min_known_source_port),
                        socket.htons(self.port_steps[new_peer]),
                        socket.htons(peer_number))
                else:
                    # Send the port of self.extra_socket to determine the
                    # currently allocated source port of the incorporated peer
                    message = peer_id.encode() + struct.pack( \
                        "4sHHHH", socket.inet_aton(new_peer[0]),
                        socket.htons(min_known_source_port),
                        socket.htons(self.port_steps[new_peer]),
                        socket.htons(peer_number),
                        socket.htons(extra_listen_port))

            # Hopefully one of these packets arrives
            self.message_queue.put((message, peer))
            self.message_queue.put((message, peer))
            self.message_queue.put((message, peer))

        # Send packets to peers currently being incorporated
        for inc_peer_id in self.incorporating_peers:
            if inc_peer_id == peer_id:
                # Do not send the peer endpoint to the peer itself
                continue
            if __debug__:
                _p_("Sending peer %s to %s" % (new_peer, inc_peer_id))
            peer = self.incorporating_peers[inc_peer_id][0]
            # Send the length of the peer_list as peer_number
            message = peer_id.encode() + struct.pack( \
                "4sHHH", socket.inet_aton(new_peer[0]),
                socket.htons(min_known_source_port),
                socket.htons(self.port_steps[new_peer]),
                socket.htons(len(self.peer_list)))
            # Hopefully one of these packets arrives
            self.message_queue.put((message, peer))
            self.message_queue.put((message, peer))
            self.message_queue.put((message, peer))

        # }}}

    def retry_to_incorporate_peer(self, peer_id):
        # {{{

        # Update source port information
        peer, start_time, source_port_to_splitter, source_ports_to_monitors, \
            serve_socket = self.incorporating_peers[peer_id]
        self.update_port_step(peer, source_port_to_splitter)
        for source_port_to_monitor in source_ports_to_monitors:
            self.update_port_step(peer, source_port_to_monitor)
        # Update peer lists
        new_peer = (peer[0], source_port_to_splitter)
        self.ids[new_peer] = self.ids.pop(peer)
        self.port_steps[new_peer] = self.port_steps.pop(peer)
        self.incorporating_peers[peer_id] = (new_peer, start_time, 0, \
            [0]*self.MONITOR_NUMBER, serve_socket)

        # Send the updated endpoint to the existing peers
        self.send_new_peer(peer_id, new_peer, source_ports_to_monitors)

        # Send all peers to the retrying peer
        try:
            self.send_the_list_of_peers_2(serve_socket, new_peer)
        except Exception as e:
            _p_("%s" % e)

        # }}}

    def update_port_step(self, peer, source_port):
        # {{{

        # Set last known source port
        self.last_source_port[peer] = source_port
        # Skip check if measured port step is 0
        if self.port_steps[peer] == 0:
            return
        if self.port_steps[peer] == None:
            self.port_steps[peer] = 0
        # Update source port information
        port_diff = abs(peer[1] - source_port)
        previous_port_step = self.port_steps[peer]
        self.port_steps[peer] = gcd(previous_port_step, port_diff)
        if self.port_steps[peer] != previous_port_step and __debug__:
            _p_('Updated port step of peer %s from %d to %d' %
                (peer, previous_port_step, self.port_steps[peer]))

        # }}}

    def remove_peer(self, peer):
        # {{{

        Splitter_DBS.remove_peer(self, peer)

        try:
            del self.ids[peer]
            del self.port_steps[peer]
            del self.last_source_port[peer]
        except KeyError:
            pass

        # }}}

    def moderate_the_team(self):
        # {{{

        while self.alive:
            # {{{

            try:
                # Allow for long messages
                message, sender = self.team_socket.recvfrom(2048)
            except:
                _p_("Unexpected error:", sys.exc_info()[0])
                continue

            _p_("Message length = %d" % len(message))

            if len(message) == 2:

                # {{{ The peer complains about a lost chunk.

                # In this situation, the splitter counts the number of
                # complains. If this number exceeds a threshold, the
                # unsupportive peer is expelled from the
                # team.

                lost_chunk_number = self.get_lost_chunk_number(message)
                self.process_lost_chunk(lost_chunk_number, sender)

                # }}}

            elif message == b'G': # 'G'oodbye

                # {{{ The peer wants to leave the team.

                self.process_goodbye(sender)

                # }}}

            elif len(message) == Common.PEER_ID_LENGTH:

                # Packet is from the arriving peer itself
                peer_id = message.decode()

                _p_("Received [hello, I'm %s] from %s" % (peer_id, sender))

                # Send acknowledge
                self.message_queue.put((message, sender))
                if peer_id not in self.arriving_peers:
                    _p_('Peer ID %s is not an arriving peer' % peer_id)
                    continue

                if __debug__:
                    if self.arriving_peers[peer_id][1] != sender[0]:
                        _p_('ID %s: peer address over TCP (%s) and ' \
                             'UDP (%s) is different' % ( \
                             peer_id, self.arriving_peers[peer_id][1], sender[0]))

                source_port_to_splitter = sender[1]

                # Update peer information
                _p_("Updating peer %s" % peer_id)

                self.arriving_peers[peer_id] = \
                    self.arriving_peers[peer_id][:2] \
                    + (source_port_to_splitter,) \
                    + self.arriving_peers[peer_id][3:]

                _p_("self.arriving_peers[peer_id][2] = %s" % self.arriving_peers[peer_id][2])
                _p_("self.arriving_peers[peer_id][3] = %s" % self.arriving_peers[peer_id][3])

                if self.arriving_peers[peer_id][2] != 0 and \
                    0 not in self.arriving_peers[peer_id][3]:
                    # Source ports are known, incorporate the peer
                    self.incorporate_peer(peer_id)

            elif sender in self.peer_list[:self.MONITOR_NUMBER] and \
                len(message) == Common.PEER_ID_LENGTH + struct.calcsize("H"):

                # Message is from monitor
                peer_id = message[:Common.PEER_ID_LENGTH].decode()
                _p_('Received forwarded hello (ID %s) from %s' % (peer_id, sender))

                # Send acknowledge
                self.message_queue.put((message, sender))
                if peer_id not in self.arriving_peers:
                    _p_('Peer ID %s is not an arriving peer' % peer_id)
                    continue

                source_port_to_monitor = struct.unpack( \
                    "H", message[Common.PEER_ID_LENGTH:])[0]
                source_port_to_monitor = socket.ntohs(source_port_to_monitor)

                # Get monitor number
                index = self.peer_list.index(sender)

                # Update peer information
                self.arriving_peers[peer_id][3][index] = source_port_to_monitor

                if self.arriving_peers[peer_id][2] != 0 and \
                    0 not in self.arriving_peers[peer_id][3]:
                    # All source ports are known, incorporate the peer
                    self.incorporate_peer(peer_id)

            elif len(message) == Common.PEER_ID_LENGTH + struct.calcsize("H"):

                # Received source port of a peer from another peer
                peer_id = message[:Common.PEER_ID_LENGTH].decode()
                _p_('Received source port of peer %s from %s' % (peer_id, sender))

                # Send acknowledge
                self.message_queue.put((message, sender))

                peer = None
                for peer_data in self.ids.items():
                    if peer_id == peer_data[1]:
                        peer = peer_data[0]
                        break

                if peer == None:
                    _p_('Peer ID %s unknown' % peer_id)
                    continue

                source_port = struct.unpack("H", message[Common.PEER_ID_LENGTH:])[0]
                source_port = socket.ntohs(source_port)

                # Update source port information
                self.update_port_step(peer, source_port)

            elif len(message) == Common.PEER_ID_LENGTH + 1:

                # A peer succeeded or failed to be incorporated into the team
                peer_id = message[:Common.PEER_ID_LENGTH].decode()

                # Send acknowledge
                self.message_queue.put((message, sender))

                if peer_id not in self.incorporating_peers:
                    if __debug__:
                        _p_('Unknown peer %s' % peer_id)
                    continue

                # Check sender address
                if sender[0] != self.incorporating_peers[peer_id][0][0]:
                    _p_('Peer %s switched from %s to %s, ignoring' \
                          % (peer_id,
                             self.incorporating_peers[peer_id][0][0],
                             sender[0]))
                    continue

                if message[-1] == b'Y'[0]:

                    _p_('Peer %s successfully incorporated' % peer_id)

                    # Close TCP socket
                    self.incorporating_peers[peer_id][4].close()
                    self.insert_peer(self.incorporating_peers[peer_id][0])
                    del self.incorporating_peers[peer_id]

                else:

                    if sender[1] == self.incorporating_peers[peer_id][0][1]:

                        # This could be due to a duplicate UDP packet
                        _p_('Peer %s retries incorporation from ' 'same port, ignoring' % peer_id)
                        continue

                    _p_('Peer %s retries incorporation from %s' % (peer_id, sender))

                    source_port_to_splitter = sender[1]

                    # Update peer information
                    self.incorporating_peers[peer_id] = \
                        self.incorporating_peers[peer_id][:2] \
                        + (source_port_to_splitter,) \
                        + self.incorporating_peers[peer_id][3:]

                    if self.incorporating_peers[peer_id][2] != 0 and \
                        0 not in self.incorporating_peers[peer_id][3]:
                        # All source ports are known, incorporate the peer
                        self.retry_to_incorporate_peer(peer_id)

            elif sender in self.peer_list[:self.MONITOR_NUMBER] and \
                len(message) == Common.PEER_ID_LENGTH+1 + struct.calcsize("H"):

                # Message is from monitor
                peer_id = message[:Common.PEER_ID_LENGTH].decode()
                _p_('Received forwarded retry hello (ID %s)' % (peer_id,))

                # Send acknowledge
                self.message_queue.put((message, sender))
                if peer_id not in self.incorporating_peers:
                    _p_('Peer ID %s is not an incorporating peer' % peer_id)
                    continue

                source_port_to_monitor = struct.unpack( \
                    "H", message[Common.PEER_ID_LENGTH+1:])[0]
                source_port_to_monitor = socket.ntohs(source_port_to_monitor)

                # Get monitor number
                index = self.peer_list.index(sender)

                # Update peer information
                self.incorporating_peers[peer_id][3][index] = source_port_to_monitor

                if self.incorporating_peers[peer_id][2] != 0 and \
                    0 not in self.incorporating_peers[peer_id][3]:
                    # All source ports are known, incorporate the peer
                    self.retry_to_incorporate_peer(peer_id)

            else:
                _p_('Ignoring packet of length %d from %s' % (len(message), sender))

            # }}}

        # }}}

    # }}}
