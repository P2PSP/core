# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

import sys
import threading
from peer_dbs import Peer_DBS
from monitor_dbs import Monitor_DBS
from peer_fns import Peer_FNS
from _print_ import _print_
from color import Color

# }}}

# FNS: Full-cone Nat Set of rules
class Monitor_FNS(Peer_FNS, Monitor_DBS):
    # {{{

    def __init__(self, peer):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Monitor FNS")
        sys.stdout.write(Color.none)

        # }}}

    def say_hello(self, node):
        # {{{

        Peer_FNS.say_hello(self, node)

        # }}}

    def say_goodbye(self, node):
        # {{{

        Peer_FNS.say_goodbye(self, node)

        # }}}

    def disconnect_from_the_splitter(self):
        # {{{

        Peer_FNS.disconnect_from_the_splitter(self)

        # }}}

    # }}}
