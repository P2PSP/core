# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{

import common
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
            for message_data in self.hello_messages:
                # Check for timeout
                if now - self.hello_messages_times[message_data] > common.MAX_PEER_ARRIVING_TIME:
                    messages_to_remove.append(message_data)
                    continue
                message, peer = message_data
                print("NTS: Sending hello (%s) to %s"
                    % (message[:common.PEER_ID_LENGTH], peer))
                for port in self.hello_messages_ports[message_data]:
                    self.team_socket.sendto(message, (peer[0], port))
                    # Avoid network congestion
                    time.sleep(0.001)
            # Remove messages that timed out
            with self.hello_messages_lock:
                for message_data in messages_to_remove:
                    if message_data in self.hello_messages:
                        print("NTS: Removed message (%s) to %s due to timeout\n"
                            % message_data)
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

        # The monitor peer endpoint has already been received
        assert len(self.peer_list) == 1

        sys.stdout.write(Color.green)
        _print_("NTS: Requesting the number of peers from splitter")
        sys.stdout.write(Color.none)
        # Add 1 as the monitor peer was already received
        self.number_of_peers = socket.ntohs(struct.unpack("H",
            self.splitter_socket.recv(struct.calcsize("H")))[0]) + 1
        _print_("NTS: The size of the team is %d (apart from me)" % self.number_of_peers)

        # Skip the monitor peer
        for _ in range(self.number_of_peers - 1):
            message = self.splitter_socket.recv(common.PEER_ID_LENGTH +
                                                struct.calcsize("4sHH"))
            peer_id = message[:common.PEER_ID_LENGTH]
            IP_addr, port, port_step = \
                struct.unpack("4sHH", message[common.PEER_ID_LENGTH:]) # Ojo, !H ????
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            peer = (IP_addr, port)
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

        self.start_send_hello_thread()

        # Receive the generated ID for this peer from splitter
        self.receive_id()

        # Note: This peer is *not* the monitor peer.

        # Send UDP packets to splitter and monitor peer
        # to create working NAT entries and to determine the
        # source port allocation type of the NAT of this peer
        self.say_hello(self.peer_list[0])
        self.say_hello(self.splitter)
        # Directly start packet sending
        self.hello_messages_event.set()

        # Receive the list of peers, except the monitor peer, with their peer IDs
        self.receive_the_list_of_peers_2()

        # Close the TCP socket
        Peer_DBS.disconnect_from_the_splitter(self)

        # }}}

    def get_probable_source_ports(self, source_port_to_splitter, port_diff, peer_number):
        # {{{

        # Predict porobable source ports that the arriving peer will use
        # to communicate with this peer

        probable_source_port = source_port_to_splitter + peer_number*port_diff
        if port_diff <= 0 or probable_source_port >= 65536:
            # Constant source port (Cone NAT) or source port prediction impossible
            return []

        # Simple port prediction: Assume port step of 1 and try port range
        return list(range(probable_source_port,
            probable_source_port + common.MAX_PREDICTED_PORTS + 1))

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
                len(message) == common.PEER_ID_LENGTH + struct.calcsize("H")):
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
            print("NTS: Received hello (ID %s) from %s" % (message, sender))
            if sender not in self.peer_list:
                self.peer_list.append(sender)
                self.debt[sender] = 0
                # Send source port information to splitter
                message += struct.pack("H", socket.htons(sender[1]))
                message_data = (message, self.splitter)
                self.send_message(message_data)
            # Send acknowledge
            self.team_socket.sendto(message, sender)
        elif message == 'H':
            # Ignore hello messages that are sent by Peer_DBS instances
            # in receive_the_list_of_peers() before a Peer_NTS instance is created
            pass
        elif sender != self.splitter and sender not in self.peer_list:
            print("NTS: Ignoring message of length %d from unknown host %s" % (len(message), sender))
        else:
            return Peer_DBS.process_message(self, message, sender)

    # }}}

    # }}}
