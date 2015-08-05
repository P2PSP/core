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

    def say_hello(self, peer):
        # {{{

        with self.hello_messages_lock:
            message = self.peer_id
            if peer == self.splitter:
                # Send the local source port to splitter
                source_port_local = self.team_socket.getsockname()[1]
                message += struct.pack("H", socket.htons(source_port_local))
            hello_data = (message, peer)
            if hello_data not in self.hello_messages:
                self.hello_messages.append(hello_data)
                self.hello_messages_times[hello_data] = time.time()
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
                self.team_socket.sendto(message, peer)
            # Remove messages that timed out
            with self.hello_messages_lock:
                for message_data in messages_to_remove:
                    if message_data in self.hello_messages:
                        print("NTS: Removed message (%s) to %s due to timeout\n"
                            % message_data)
                        self.hello_messages.remove(message_data)
                        del self.hello_messages_times[message_data]

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
        # Start the hello packet sending thread
        threading.Thread(target=self.send_hello_thread).start()

        # }}}

    def receive_the_list_of_peers_2(self):
        # {{{

        self.debt = {}      # Chunks debts per peer.
        self.peer_list = [] # The list of peers structure.

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
                                                struct.calcsize("4sH"))
            peer_id = message[:common.PEER_ID_LENGTH]
            IP_addr, port = struct.unpack("4sH", message[common.PEER_ID_LENGTH:]) # Ojo, !H ????
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            peer = (IP_addr, port)
            print("NTS: [hello] sent to %s" % (peer,))
            self.say_hello(peer)

            self.peer_list.append(peer)
            self.debt[peer] = 0

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

        # Receive the list of peers, except the monitor peer, with their peer IDs
        self.receive_the_list_of_peers_2()

        # Close the TCP socket
        Peer_DBS.disconnect_from_the_splitter(self)

        # }}}

    def process_message(self, message, sender):
        # {{{ Handle NTS messages; pass other messages to base class

        if sender == self.splitter and \
                len(message) == common.PEER_ID_LENGTH + struct.calcsize("4sH"):
            # [say hello to (X)] received from splitter
            peer_id = message[:common.PEER_ID_LENGTH]
            IP_addr, port = struct.unpack("4sH", message[common.PEER_ID_LENGTH:]) # Ojo, !H ????
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            peer = (IP_addr, port)
            print("NTS: Received [send hello to %s %s]" % (peer_id, peer))
            self.say_hello(peer)
        elif message == self.peer_id or (sender == self.splitter and \
                len(message) == common.PEER_ID_LENGTH + struct.calcsize("H")):
            print("NTS: Received acknowledge from %s" % (sender,))
            with self.hello_messages_lock:
                hello_data = (message, sender)
                if hello_data in self.hello_messages:
                    self.hello_messages.remove(hello_data)
                    del self.hello_messages_times[hello_data]
        elif len(message) == common.PEER_ID_LENGTH:
            print("NTS: Received hello (ID %s) from %s" % (message, sender))
            if sender not in self.peer_list:
                self.peer_list.append(sender)
                self.debt[sender] = 0
            # Send acknowledge
            self.team_socket.sendto(message, sender)
        elif message == 'H':
            # Ignore hello messages that are sent by Peer_DBS instances
            # in receive_the_list_of_peers() before a Peer_NTS instance is created
            pass
        else:
            return Peer_DBS.process_message(self, message, sender)

    # }}}

    # }}}
