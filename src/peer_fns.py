# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

import threading
import sys
from peer_dbs import Peer_DBS
from _print_ import _print_
from color import Color

# }}}

# FNS: Full-cone Nat Set of rules
class Peer_FNS(Peer_DBS):
    # {{{

    def __init__(self, peer):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Peer FNS")
        sys.stdout.write(Color.none)

        # }}}

    def say_hello(self, node):
        # {{{

        self.team_socket.sendto(b'H', node)

        # }}}

    def say_goodbye(self, node):
        # {{{

        self.team_socket.sendto(b'G', node)

        # }}}

    def disconnect_from_the_splitter(self):
        # {{{

        # Close the TCP socket
        Peer_DBS.disconnect_from_the_splitter(self)

        # Use UDP to create a working NAT entry
        self.say_hello(self.splitter)
        self.say_hello(self.splitter)
        self.say_hello(self.splitter)

        # }}}
        
    # }}}
