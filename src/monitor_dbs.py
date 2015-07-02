# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

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
        _print_("Monitor DBS (list)")
        sys.stdout.write(Color.none)

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
