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

    def say_hello(self, node):
        # {{{

        print("NTS: Sending hello (ID %s) to %s" % (self.peer_id, node))
        self.team_socket.sendto(self.peer_id, node)

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

    def disconnect_from_the_splitter(self):
        # {{{

        # Receive the generated ID for this peer from splitter
        self.receive_id()

        # Close the TCP socket
        Peer_DBS.disconnect_from_the_splitter(self)

        # Use UDP to create a working NAT entry
        self.say_hello(self.splitter)

        # }}}

    def process_message(self, message, sender):
        # {{{ Handle NTS messages; pass other messages to base class

        if len(message) == struct.calcsize("4sH"):
            # [say hello to (X)] received from splitter
            IP_addr, port = struct.unpack("4sH", message)
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            peer = (IP_addr, port)
            print("NTS: received [send hello to %s]" % (peer,))
            print("NTS: sending [hello] to %s" % (peer,))
            self.say_hello(peer)

            self.peer_list.append(peer)
            self.debt[peer] = 0
        else:
            return Peer_DBS.process_message(self, message, sender)

    # }}}

    # }}}
