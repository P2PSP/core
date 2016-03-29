"""
@package core
monitor_dbs module
"""

# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# DBS: Data Broadcasting Set of rules

# {{{ Imports

import sys
import socket
import struct
import threading

from core.common import Common

from core.peer_ims import Peer_IMS
from core.peer_dbs import Peer_DBS
from core._print_ import _print_
from core.color import Color

# }}}

def _p_(*args, **kwargs):
    if __debug__:
        """Colorize the output."""
        sys.stdout.write(Common.DBS_COLOR)
        _print_("DBS:", *args)
        sys.stdout.write(Color.none)

class Monitor_DBS(Peer_DBS):
    # {{{

    def __init__(self, peer):
        # {{{

        _p_("Initialized")

        # }}}

    #def print_the_module_name(self):
        # {{{

        #sys.stdout.write(Color.red)
        #_print_("Monitor DBS")
        #sys.stdout.write(Color.none)

        # }}}

    def complain(self, chunk_number):
        # {{{

        message = struct.pack("!H", chunk_number)
        self.team_socket.sendto(message, self.splitter)

        _p_ ("lost chunk:", chunk_number)
            
        # }}}

    def find_next_chunk(self):
        # {{{

        chunk_number = (self.played_chunk + 1) % Common.MAX_CHUNK_NUMBER
        while not self.received_flag[chunk_number % self.buffer_size]:
            self.complain(chunk_number)
            chunk_number = (chunk_number + 1) % Common.MAX_CHUNK_NUMBER
        return chunk_number

        # }}}

    # }}}
