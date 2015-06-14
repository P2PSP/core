# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucía
# through the Proyecto Motriz "Codificación de Vídeo Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports
import threading
import sys
import socket
from peer_fns import Peer_FNS
from color import Color
from _print_ import _print_
from lossy_socket import lossy_socket
# }}}

# Some useful definitions.
ADDR = 0
PORT = 1

class Lossy_Peer(Peer_FNS):
    # {{{

    CHUNK_LOSS_PERIOD = 10

    def __init__(self, peer):
        # {{{

        #Peer_FNS.__init__(self, peer)

        sys.stdout.write(Color.yellow)
        _print_("Lossy Peer")
        sys.stdout.write(Color.none)

        threading.Thread.__init__(self)

        self.splitter_socket = peer.splitter_socket
        self.player_socket = peer.player_socket
        self.buffer_size = peer.buffer_size
        self.chunk_format_string = peer.chunk_format_string
        self.splitter = peer.splitter
        self.chunk_size = peer.chunk_size
        self.peer_list = peer.peer_list
        self.debt = peer.debt

        # }}}

    def print_the_module_name(self):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Lossy Peer")
        sys.stdout.write(Color.none)

        # }}}

    def listen_to_the_team(self):
        # {{{ Create "team_socket" (UDP) as a copy of "splitter_socket" (TCP)

        self.team_socket = lossy_socket(self.CHUNK_LOSS_PERIOD, socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # In Windows systems this call doesn't work!
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception as e:
            print (e)
            pass
        self.team_socket.bind(('', self.splitter_socket.getsockname()[PORT]))

        # This is the maximum time the peer will wait for a chunk
        # (from the splitter or from another peer).
        self.team_socket.settimeout(1)

        # }}}

    # }}}
