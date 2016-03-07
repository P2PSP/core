"""
@package core
splitter_lrs module
"""

# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# LRS: Lost chunk Recovery Set of rules

# {{{ Imports

from __future__ import print_function
import threading
import sys
import socket
import struct
import time

from core.common import Common
from core.color import Color
from core._print_ import _print_
#from splitter_ims import Splitter_IMS
from core.splitter_dbs import Splitter_DBS
#from splitter_fns import Splitter_FNS
#from splitter_acs import Splitter_ACS

# }}}

def _p_(*args, **kwargs):
    """Colorize the output."""
    if __debug__:
        sys.stdout.write(Common.LRS_COLOR)
        _print_("LRS:", *args)
        sys.stdout.write(Color.none)

class Splitter_LRS(Splitter_DBS):
    # {{{

    def __init__(self, splitter):
        # {{{

        #Splitter_ACS.__init__(self)
        #sys.stdout.write(Color.yellow)
        #print("Using LRS")
        #sys.stdout.write(Color.none)

        # Massively lost chunks are retransmitted. So, the splitter
        # needs to remember the chunks sent recently. Buffer is A
        # circular array of messages (chunk_number, chunk) in network
        # endian format.
        self.buffer = [""]*self.BUFFER_SIZE
        self.magic_flags |= Common.LRS

        _p_("Initialized")
        
        # }}}

    def process_lost_chunk(self, lost_chunk_number, sender):
        # {{{

        Splitter_DBS.process_lost_chunk(self, lost_chunk_number, sender)
        message = self.buffer[lost_chunk_number % self.BUFFER_SIZE]
        peer = self.peer_list[0]
        self.team_socket.sendto(message, peer)
        if __debug__:
            #sys.stdout.write(Color.cyan)
            _p_("Re-sending", lost_chunk_number, "to", peer)
            #sys.stdout.write(Color.none)

        # }}}

    def send_chunk(self, message, peer):
        # {{{

        Splitter_DBS.send_chunk(self, message, peer)
        self.buffer[self.chunk_number % self.BUFFER_SIZE] = message

        # }}}


    # }}}
