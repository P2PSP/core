# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{

import common
import math
import threading
import time
import sys
import struct
import socket
from color import Color
from _print_ import _print_
from peer_dbs import Peer_DBS

# }}}

# NTS: NAT Traversal Set of rules
class Peer_NTS(Peer_DBS):
    # {{{

    def __init__(self, peer):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Peer NTS")
        sys.stdout.write(Color.none)

        # }}}

    def say_hello(self, peer, additional_ports=[]):
        # {{{

        with self.hello_messages_lock:
            message = self.peer_id
            hello_data = (message, peer)
            if hello_data not in self.hello_messages:
                self.hello_messages.append(hello_data)
                self.hello_messages_times[hello_data] = time.time()
                self.hello_messages_ports[hello_data] = additional_ports+[peer[1]]

        # }}}

    def send_message(self, message_data):
        # {{{ Parameter: message_data = (message, destination)
        # Send a general message continuously until acknowledge is received

        with self.hello_messages_lock:
            if message_data not in self.hello_messages:
                self.hello_messages.append(message_data)
                self.hello_messages_times[message_data] = time.time()
                self.hello_messages_ports[message_data] = [message_data[1][1]]
                # Directly start packet sending
                self.hello_messages_event.set()

        # }}}

    def say_goodbye(self, node):
        # {{{

        self.team_socket.sendto(b'G', node)

        # }}}

    def receive_id(self):
        # {{{

        _print_("NTS: Requesting peer ID from splitter")
        self.peer_id = self.splitter_socket.recv(common.PEER_ID_LENGTH)
        _print_("NTS: ID received: %s" % self.peer_id)

        # }}}

    def send_hello_thread(self):
        # {{{

        while self.player_alive:
            # Continuously send hello UDP packets to arriving peers
            # until a connection is established
            now = time.time()
            messages_to_remove = []
            # Make local copies as entries may be removed
            hello_messages = self.hello_messages[:]
            hello_messages_times = self.hello_messages_times.copy()
            hello_messages_ports = self.hello_messages_ports.copy()
            for message_data in hello_messages:
                # Check for timeout
                if now - hello_messages_times[message_data] > common.MAX_PEER_ARRIVING_TIME:
                    messages_to_remove.append(message_data)
                    continue
                message, peer = message_data
                if message == self.peer_id:
                    print("NTS: Sending hello (%s) to %s (trying %d ports)"
                        % (message, peer, len(hello_messages_ports[message_data])))
                else:
                    print("NTS: Sending message (%s) of length %d to %s (trying %d ports)"
                        % (message[:common.PEER_ID_LENGTH], len(message), peer,
                        len(hello_messages_ports[message_data])))
                for port in hello_messages_ports[message_data]:
                    self.team_socket.sendto(message, (peer[0], port))
                    # Avoid network congestion
                    time.sleep(0.001)
            # Remove messages that timed out
            with self.hello_messages_lock:
                for message_data in messages_to_remove:
                    if message_data in self.hello_messages:
                        print("NTS: Removed message (%s) to %s due to timeout\n"
                            % (message_data[0][:common.PEER_ID_LENGTH], message_data[1]))
                        self.hello_messages.remove(message_data)
                        del self.hello_messages_times[message_data]
                        del self.hello_messages_ports[message_data]

            self.hello_messages_event.clear()
            self.hello_messages_event.wait(common.HELLO_PACKET_TIMING)

        # }}}

    def start_send_hello_thread(self):
        # {{{

        self.player_alive = True # Peer_IMS sets this variable in buffer_data()
        self.hello_messages = [] # Each entry is a (peer_endpoint, message) tuple
        self.hello_messages_lock = threading.Lock()
        self.hello_messages_event = threading.Event()
        self.hello_messages_times = {} # Start times of the messages
        self.hello_messages_ports = {} # Ports to send the message to
        # Start the hello packet sending thread
        threading.Thread(target=self.send_hello_thread).start()

        # }}}

    def receive_the_list_of_peers_2(self):
        # {{{

        # The monitor peer endpoints have already been received
        assert len(self.peer_list) == self.number_of_monitors

        sys.stdout.write(Color.green)
        _print_("NTS: Requesting the number of peers from splitter")
        sys.stdout.write(Color.none)
        # Add 1 as the monitor peer was already received
        self.number_of_peers = socket.ntohs(struct.unpack("H",
            self.splitter_socket.recv(struct.calcsize("H")))[0]) + self.number_of_monitors
        _print_("NTS: The size of the team is %d (apart from me)" % self.number_of_peers)

        # Skip the monitor peer
        for _ in range(self.number_of_peers - self.number_of_monitors):
            message = self.splitter_socket.recv(common.PEER_ID_LENGTH +
                                                struct.calcsize("4sHH"))
            peer_id = message[:common.PEER_ID_LENGTH]
            IP_addr, port, port_step = \
                struct.unpack("4sHH", message[common.PEER_ID_LENGTH:]) # Ojo, !H ????
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            port_step = socket.ntohs(port_step)
            peer = (IP_addr, port)

            self.initial_peer_list.append(peer_id)

            # Try different probable ports for the existing peer
            probable_source_ports = []
            if port_step > 0:
                number_of_ports = min((65536-port)//port_step, common.MAX_PREDICTED_PORTS)
                probable_source_ports = list(range(port+port_step,
                    port+(number_of_ports+1)*port_step, port_step))
            self.say_hello(peer, probable_source_ports)
            print("NTS: [hello] sent to %s" % (peer,))

        # Directly start packet sending
        self.hello_messages_event.set()

        sys.stdout.write(Color.green)
        _print_("NTS: List of peers received")
        sys.stdout.write(Color.none)

        # }}}

    def disconnect_from_the_splitter(self):
        # {{{

        try:
            self.try_to_disconnect_from_the_splitter()
        except Exception as e:
            sys.stderr.write(
                "NTS: '%s': Probably the splitter removed this peer due to timeout\n" % e)
            self.player_alive = False
            sys.exit(1)

        # }}}

    def try_to_disconnect_from_the_splitter(self):
        # {{{

        self.start_send_hello_thread()

        # Receive the generated ID for this peer from splitter
        self.receive_id()

        # Note: This peer is *not* the monitor peer.

        # Send UDP packets to splitter and monitor peers
        # to create working NAT entries and to determine the
        # source port allocation type of the NAT of this peer
        for peer in self.peer_list[:self.number_of_monitors]:
            self.say_hello(peer)
        self.say_hello(self.splitter)
        # Directly start packet sending
        self.hello_messages_event.set()

        # A list of peer_ids that contains the peers that were in the team when
        # starting incorporation and that are not connected yet
        self.initial_peer_list = []
        # Receive the list of peers, except the monitor peer, with their peer IDs
        # and send hello messages
        self.receive_the_list_of_peers_2()

        # Wait for getting connected to all currently known peers
        incorporation_time = time.time()
        # A timeout less than common.MAX_PEER_ARRIVING_TIME has to be set for self.team_socket
        # The monitor is not in initial_peer_list
        while len(self.initial_peer_list) > 0:
            if time.time() - incorporation_time > common.MAX_PEER_ARRIVING_TIME:
                # Retry incorporation into the team
                print("NTS: Timed out with %d peers left to connect. Retrying incorporation." \
                    % len(self.initial_peer_list))
                incorporation_time = time.time()
                # Cleaning hello messages
                with self.hello_messages_lock:
                    self.hello_messages_times.clear()
                    self.hello_messages_ports.clear()
                    del self.hello_messages[:]
                # Resetting peer lists
                del self.initial_peer_list[:]
                del self.peer_list[self.number_of_monitors:] # Leave monitors in list
                # Recreate the socket
                # This similar to Peer_DBS.listen_to_the_team, but binds to a new random port
                self.team_socket.close()
                self.team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                except Exception as e:
                    print ("NTS:", e)
                    pass
                self.team_socket.bind(('', 0))
                self.team_socket.settimeout(1)
                # Say hello to splitter again, to retry incorporation
                # 'N' for 'not incorporated'
                self.send_message((self.peer_id + 'N', self.splitter))
                # Say hello to monitors again, to keep the NAT entry alive
                for peer in self.peer_list[:self.number_of_monitors]:
                    self.send_message((self.peer_id + 'N', peer))
                # Receive all peer endpoints and send hello messages
                self.receive_the_list_of_peers_2()

            # Process messages to establish connections to peers
            try:
                message, sender = self.team_socket.recvfrom(struct.calcsize(self.message_format))
                self.process_message(message, sender)
            except socket.timeout:
                pass

        # Close the TCP socket
        Peer_DBS.disconnect_from_the_splitter(self)
        # The peer is now successfully incorporated; inform the splitter
        self.send_message((self.peer_id + 'Y', self.splitter))

        # }}}

    def get_factors(self, n):
        # {{{ This function is from http://stackoverflow.com/a/6800214

        return sorted(set(reduce(list.__add__,
            ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0))))

        # }}}

    def count_combinations(self, factors):
        # {{{

        # Get the number of possible products of a factor and another integer
        # that are less or equal to the original number n.
        # Example: the number is 10, the factors are 1, 2, 5, 10.
        # Products <=10: 1*1, ..., 1*10, 2*1, ..., 2*5, 5*1, 5*2, 10*1.
        # So for each factor there are "n/factor" products:
        return reduce(lambda a, b: a + b, factors)

        # }}}

    def get_probable_port_diffs(self, port_diff, peer_number):
        # {{{

        # The actual port prediction happens here:
        # port_diff is the measured source port difference, so the NAT could have
        # any factor of port_diff as its actual port_step. This function assumes
        # different port_step values and calculates a few resulting source port
        # differences, assuming some ports are skipped (already taken).

        factors = self.get_factors(port_diff)
        num_combinations = self.count_combinations(factors)
        count_factor = common.MAX_PREDICTED_PORTS/float(num_combinations)

        port_diffs = sorted(set(reduce(list.__add__, (list(
            # For each previous peer and each skip, the source port is incremented
            port_step * (peer_number + skips)
            # For each assumed port_step, "port_diff/port_step" different port skips
            # are tried, multiplied with count_factor to get the desired list length
            for skips in range(int(math.ceil(port_diff/port_step*count_factor))+1))
            # Each factor of port_diff is a possible port_step
            for port_step in factors))))
        return port_diffs

        # }}}

    def get_probable_source_ports(self, source_port_to_splitter, port_diff, peer_number):
        # {{{

        # Predict porobable source ports that the arriving peer will use
        # to communicate with this peer

        if port_diff <= 0:
            # Constant source port (Cone NAT)
            return []

        # Port prediction:
        return list(source_port_to_splitter + probable_port_diff
            for probable_port_diff in self.get_probable_port_diffs(port_diff, peer_number)
            if source_port_to_splitter + probable_port_diff < 65536)

        # }}}

    def process_message(self, message, sender):
        # {{{ Handle NTS messages; pass other messages to base class

        if sender == self.splitter and \
                len(message) == common.PEER_ID_LENGTH + struct.calcsize("4sHHH"):
            # [say hello to (X)] received from splitter
            peer_id = message[:common.PEER_ID_LENGTH]
            IP_addr, source_port_to_splitter, port_diff, peer_number = \
                struct.unpack("4sHHH", message[common.PEER_ID_LENGTH:]) # Ojo, !H ????
            IP_addr = socket.inet_ntoa(IP_addr)
            source_port_to_splitter = socket.ntohs(source_port_to_splitter)
            port_diff = socket.ntohs(port_diff)
            peer_number = socket.ntohs(peer_number)

            peer = (IP_addr, source_port_to_splitter) # Peer endpoint known to splitter
            print("NTS: Received [send hello to %s %s]" % (peer_id, peer))
            # Here the port prediction happens:
            additional_ports = self.get_probable_source_ports(source_port_to_splitter,
                port_diff, peer_number)
            self.say_hello(peer, additional_ports)
            # Directly start packet sending
            self.hello_messages_event.set()
        elif message == self.peer_id or (sender == self.splitter and \
                len(message) == common.PEER_ID_LENGTH + struct.calcsize("H")) or \
                (sender == self.splitter and \
                len(message) == common.PEER_ID_LENGTH+1 + struct.calcsize("H")) or \
                len(message) == common.PEER_ID_LENGTH+1:
            with self.hello_messages_lock:
                for hello_data in self.hello_messages:
                    if message == hello_data[0] and sender[0] == hello_data[1][0] \
                            and sender[1] in self.hello_messages_ports[hello_data]:
                        print("NTS: Received acknowledge from %s" % (sender,))
                        self.hello_messages.remove(hello_data)
                        del self.hello_messages_times[hello_data]
                        del self.hello_messages_ports[hello_data]
                        return
            print("NTS: Received acknowledge from unknown host %s" % (sender,))
        elif len(message) == common.PEER_ID_LENGTH:
            peer_id = message
            print("NTS: Received hello (ID %s) from %s" % (message, sender))
            # Send acknowledge
            self.team_socket.sendto(message, sender)

            if sender not in self.peer_list:
                self.peer_list.append(sender)
                self.debt[sender] = 0
                # Send source port information to splitter
                message += struct.pack("H", socket.htons(sender[1]))
                message_data = (message, self.splitter)
                self.send_message(message_data)

                if peer_id in self.initial_peer_list:
                    self.initial_peer_list.remove(peer_id)
        elif message == 'H':
            # Ignore hello messages that are sent by Peer_DBS instances
            # in receive_the_list_of_peers() before a Peer_NTS instance is created
            pass
        elif sender != self.splitter and sender not in self.peer_list:
            print("NTS: Ignoring message of length %d from unknown host %s" % (len(message), sender))
        elif len(self.initial_peer_list) == 0: # Start receiving chunks when fully incorporated
            return Peer_DBS.process_message(self, message, sender)

    # }}}

    # }}}
