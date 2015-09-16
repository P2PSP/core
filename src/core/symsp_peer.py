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
from peer_dbs import Peer_DBS
from color import Color
from symsp_socket import symsp_socket

# }}}

# Some useful definitions.
ADDR = 0
PORT = 1

class Symsp_Peer(Peer_DBS):
    # {{{

    PORT_STEP = 0

    def __init__(self, peer):
        # {{{

        sys.stdout.write(Color.yellow)
        sys.stdout.write("Symsp Peer\n")
        sys.stdout.write(Color.none)

        # }}}

    def listen_to_the_team(self):
        # {{{ Create "team_socket" (UDP) as a copy of "splitter_socket" (TCP)

        # Create a special socket to force source port increment on SYMSP NATs
        self.team_socket = symsp_socket(self.PORT_STEP, socket.AF_INET,
                                        socket.SOCK_DGRAM)
        try:
            # In Windows systems this call doesn't work!
            self.team_socket.setsockopt( \
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception as e:
            print ("NTS:", e)
        self.team_socket.bind(('', self.splitter_socket.getsockname()[PORT]))

        # This is the maximum time the peer will wait for a chunk
        # (from the splitter or from another peer).
        self.team_socket.settimeout(1)

        # }}}

    # }}}
