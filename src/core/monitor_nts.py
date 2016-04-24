"""
@package core
monitor_nts module
"""

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# NTS: NAT Traversal Set of rules

# {{{ Imports

import sys
import struct
import socket

from core.common import Common

from core.peer_dbs import Peer_DBS
from core.peer_nts import Peer_NTS
from core._print_ import _print_
from core.color import Color

# }}}

def _p_(*args, **kwargs):
    if __debug__:
        """Colorize the output."""
        sys.stdout.write(Common.NTS_COLOR)
        _print_("NTS:", *args)
        sys.stdout.write(Color.none)

class Monitor_NTS(Peer_NTS):
    # {{{

    def __init__(self, peer):
        # {{{

        _p_("Initialized")

        # }}}

    def complain(self, chunk_number):
        # {{{ This is from Monitor_DBS

        message = struct.pack("!H", chunk_number)
        self.team_socket.sendto(message, self.splitter)

        if __debug__:
            sys.stdout.write(Color.cyan)
            print ("lost chunk:", chunk_number)
            sys.stdout.write(Color.none)

        # }}}

    def find_next_chunk(self):
        # {{{ This is from Monitor_DBS

        chunk_number = (self.played_chunk + 1) % Common.MAX_CHUNK_NUMBER
        while not self.received_flag[chunk_number % self.buffer_size]:
            self.complain(chunk_number)
            chunk_number = (chunk_number + 1) % Common.MAX_CHUNK_NUMBER
        return chunk_number

        # }}}

    # }}}

    def disconnect_from_the_splitter(self):
        # {{{

        self.start_send_hello_thread()

        # Receive the generated ID for this peer from splitter
        self.receive_id()

        # There are currently no other peers in the team
        self.initial_peer_list = []

        # Close the TCP socket
        Peer_DBS.disconnect_from_the_splitter(self)

        # }}}

    def process_message(self, message, sender):
        # {{{ Handle NTS messages; pass other messages to base class

        if sender != self.splitter and \
        (len(message) == Common.PEER_ID_LENGTH or
         len(message) == Common.PEER_ID_LENGTH+1):
            # Hello message received from peer
            if __debug__:
                print("NTS: Received hello (ID %s) from %s" \
                    % (message[:Common.PEER_ID_LENGTH], sender))
            # Send acknowledge
            self.team_socket.sendto(message, sender)

            if __debug__:
                print("NTS: Forwarding ID %s and source port %s to splitter"
                      % (message[:Common.PEER_ID_LENGTH], sender[1]))
            message += struct.pack("H", socket.htons(sender[1]))
            message_data = (message, self.splitter)
            self.send_message(message_data)
        elif sender == self.splitter and \
                len(message) == Common.PEER_ID_LENGTH + struct.calcsize("4sH"):
            # [say hello to (X)] received from splitter
            peer_id = message[:Common.PEER_ID_LENGTH].decode()
            IP_addr, port = \
                struct.unpack("4sH", message[Common.PEER_ID_LENGTH:]) # Ojo, !H?
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            peer = (IP_addr, port)
            if __debug__:
                print("NTS: Received peer ID %s %s" % (peer_id, peer))
            # Sending hello not needed as monitor and peer already communicated
            if peer not in self.peer_list:
                print("NTS: Appending peer %s %s to list" % (peer_id, peer))
                self.peer_list.append(peer)
                self.debt[peer] = 0
        else:
            return Peer_NTS.process_message(self, message, sender)

        # No chunk number, as no chunk was received
        return -1

        # }}}
