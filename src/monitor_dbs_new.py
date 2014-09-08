# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# {{{ Imports

import sys
import socket
import struct
import threading
from peer_ims import Peer_IMS
from peer_dbs import Peer_DBS
from _print_ import _print_
from color import Color
import common

# }}}

# DBS: Data Broadcasting Set of rules
class Monitor_DBS(Peer_DBS):
    # {{{

    def __init__(self, peer):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Monitor DBS (no list)")
        sys.stdout.write(Color.none)

        threading.Thread.__init__(self)

        self.peer_list = peer.peer_list
        self.splitter_socket = peer.splitter_socket
        self.buffer_size = peer.buffer_size
        self.splitter = peer.splitter
        self.debt = peer.debt
        self.chunk_size = peer.chunk_size
        self.player_socket = peer.player_socket
        self.standard_message_format = peer.standard_message_format
        self.extended_message_format = peer.extended_message_format
        self.number_of_peers = peer.number_of_peers
        
        # }}}

    def print_the_module_name(self):
        # {{{

        sys.stdout.write(Color.red)
        _print_("Monitor DBS")
        sys.stdout.write(Color.none)

        # }}}
    
    def complain(self, chunk_number):
        # {{{

        message = struct.pack("!H", chunk_number)
        self.team_socket.sendto(message, self.splitter)

        # }}}

    def find_next_chunk(self):
        # {{{

        chunk_number = (self.played_chunk + 1) % common.MAX_CHUNK_NUMBER
        while not self.received[chunk_number % self.buffer_size]:
            sys.stdout.write(Color.cyan)
            _print_("lost chunk", chunk_number)
            sys.stdout.write(Color.none)
            self.complain(chunk_number)
            chunk_number = (chunk_number + 1) % common.MAX_CHUNK_NUMBER
        return chunk_number

        # }}}

    # }}}
