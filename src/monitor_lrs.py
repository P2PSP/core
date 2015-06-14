# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucía
# through the Proyecto Motriz "Codificación de Vídeo Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

import sys
import threading
from _print_ import _print_
from monitor_fns import Monitor_FNS
from color import Color

# }}}

# LRS: Lost chunks Recovery Set of rules
class Monitor_LRS(Monitor_FNS):
    # {{{

    def __init__(self, peer):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Monitor LRS")
        sys.stdout.write(Color.none)

        threading.Thread.__init__(self)
        
        self.splitter_socket = peer.splitter_socket
        self.splitter = peer.splitter
        self.buffer_size = peer.buffer_size
        #self.chunk_format_string = peer.chunk_format_string
        self.peer_list = peer.peer_list
        self.player_socket = peer.player_socket
        self.chunk_size = peer.chunk_size
        self.debt = peer.debt
        self.team_socket = peer.team_socket
        self.message_format = peer.message_format

        # }}}

    def receive_the_buffer_size(self):
        # {{{

        message = self.splitter_socket.recv(struct.calcsize("H"))
        buffer_size = struct.unpack("H", message)[0]
        self.buffer_size = socket.ntohs(buffer_size)
        # Monitor peers that implements the LRS use a smaller buffer
        # in order to complains before the rest of peers reach them in
        # their buffers.
        self.buffer_size /= 2
        print ("buffer_size =", self.buffer_size)

        # }}}

    # }}}
