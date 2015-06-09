# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucía
# through the Proyecto Motriz "Codificación de Vídeo Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

from __future__ import print_function
import threading
import sys
import socket
import struct
import time
from color import Color
import common
from _print_ import _print_
from splitter_ims import Splitter_IMS
from splitter_dbs import Splitter_DBS
from splitter_fns import Splitter_FNS
from splitter_acs import Splitter_ACS

# }}}

# LRS: Lost chunk Recovery Set of rules
class Splitter_LRS(Splitter_ACS):
    # {{{

    def __init__(self):
        # {{{

        Splitter_ACS.__init__(self)
        sys.stdout.write(Color.yellow)
        print("Using LRS")
        sys.stdout.write(Color.none)

        # A circular array of messages (chunk_number, chunk) in
        # network endian
        self.buffer = [""]*self.BUFFER_SIZE

        # }}}

    def process_lost_chunk(self, lost_chunk_number, sender):
        # {{{

        Splitter_ACS.process_lost_chunk(self, lost_chunk_number, sender)
        message = self.buffer[lost_chunk_number % self.BUFFER_SIZE]
        peer = self.peer_list[0]
        self.team_socket.sendto(message, peer)
        if __debug__:
            sys.stdout.write(Color.cyan)
            print ("LRS: Re-sending", lost_chunk_number, "to", peer)
            sys.stdout.write(Color.none)

        # }}}

    def send_chunk(self, message, peer):
        # {{{

        Splitter_ACS.send_chunk(self, message, peer)
        self.buffer[self.chunk_number % self.BUFFER_SIZE] = message
        
        # }}}


    # }}}
