# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.

# {{{ Imports

import sys
import socket
import struct
from peer_dbs import Peer_DBS
from _print_ import _print_
from color import Color

# }}}

class Monitor_DBS(Peer_DBS):
    # {{{

    def print_the_module_name(self):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Monitor DBS")
        sys.stdout.write(Color.none)

        # }}}
    
    def __init__(self, peer):
        # {{{

        #Peer_DBS.__init__(self, peer)
        self.team_socket = peer.team_socket
        self.played_chunk = peer.played_chunk
        self.buffer_size = peer.buffer_size

        # }}}

    def complain(self, chunk_number):
        # {{{

        #message = struct.pack("!H", (chunk_number % self.buffer_size))
        message = struct.pack("!H", chunk_number)
        self.team_socket.sendto(message, self.splitter)

        if __debug__:
            sys.stdout.write(Color.blue)
            print ("lost chunk:", self.numbers[chunk_number % self.buffer_size], chunk_number, self.received[chunk_number % self.buffer_size])
            sys.stdout.write(Color.none)

        # }}}

    def find_next_chunk(self):
        # {{{

        chunk_number = (self.played_chunk + 1) % common.MAX_CHUNK_NUMBER
        while not self.received[chunk_number % self.buffer_size]:
            self.complain(chunk_number)
            chunk_number = (chunk_number + 1) % common.MAX_CHUNK_NUMBER
        return chunk_number

        # }}}

    # }}}
