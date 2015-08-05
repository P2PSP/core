# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

import sys
import struct
import socket
import time
from peer_dbs import Peer_DBS
from peer_nts import Peer_NTS
from _print_ import _print_
from color import Color
import common

# }}}

# NTS: NAT Traversal Set of rules
class Monitor_NTS(Peer_NTS):
    # {{{

    def __init__(self, peer):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Monitor NTS (list)")
        sys.stdout.write(Color.none)

        # }}}

    def print_the_module_name(self):
        # {{{

        sys.stdout.write(Color.red)
        _print_("Monitor NTS")
        sys.stdout.write(Color.none)

        # }}}

    def complain(self, chunk_number):
        # {{{

        message = struct.pack("!H", chunk_number)
        self.team_socket.sendto(message, self.splitter)

        if __debug__:
            sys.stdout.write(Color.cyan)
            print ("lost chunk:", chunk_number)
            sys.stdout.write(Color.none)

        # }}}

    def find_next_chunk(self):
        # {{{

        chunk_number = (self.played_chunk + 1) % common.MAX_CHUNK_NUMBER
        while not self.received_flag[chunk_number % self.buffer_size]:
            self.complain(chunk_number)
            chunk_number = (chunk_number + 1) % common.MAX_CHUNK_NUMBER
        return chunk_number

        # }}}

    # }}}

    def disconnect_from_the_splitter(self):
        # {{{

        self.start_send_hello_thread()

        # Receive the generated ID for this peer from splitter
        self.receive_id()

        # Close the TCP socket
        Peer_DBS.disconnect_from_the_splitter(self)

        # }}}

    def process_message(self, message, sender):
        # {{{ Handle NTS messages; pass other messages to base class

        if sender != self.splitter and len(message) == common.PEER_ID_LENGTH:
            print("NTS: Received hello (ID %s) from %s" % (message, sender))
            # Send acknowledge
            self.team_socket.sendto(message, sender)

            print("NTS: Forwarding ID %s and source port %s to splitter"
                % (message, sender[1]))
            message += struct.pack("H", socket.htons(sender[1]))
            with self.hello_messages_lock:
                message_data = (message, self.splitter)
                if message_data not in self.hello_messages:
                    self.hello_messages.append(message_data)
                    self.hello_messages_times[message_data] = time.time()
                    # Directly start packet sending
                    self.hello_messages_event.set()
        elif sender == self.splitter and \
                len(message) == common.PEER_ID_LENGTH + struct.calcsize("4sH"):
            # [say hello to (X)] received from splitter
            peer_id = message[:common.PEER_ID_LENGTH]
            IP_addr, port = struct.unpack("4sH", message[common.PEER_ID_LENGTH:]) # Ojo, !H ????
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            peer = (IP_addr, port)
            print("NTS: Received [send hello to %s %s]" % (peer_id, peer))
            # Sending hello not needed as monitor and peer already communicated
            if peer not in self.peer_list:
                self.peer_list.append(peer)
                self.debt[peer] = 0
        else:
            return Peer_NTS.process_message(self, message, sender)

        # }}}
