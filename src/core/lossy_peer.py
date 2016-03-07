"""
@package core
lossy_peer module
"""

# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# {{{ Imports

import threading
import sys
import socket

from core.common import Common
from core.color import Color
from core._print_ import _print_
from core.lossy_socket import lossy_socket
from core.peer_dbs import Peer_DBS

# }}}

# Some useful definitions.
ADDR = 0
PORT = 1

def _p_(*args, **kwargs):
    if __debug__:
        """Colorize the output."""
        sys.stdout.write(Common.DBS_COLOR)
        _print_("DBS:", *args)
        sys.stdout.write(Color.none)

class Lossy_Peer(Peer_DBS):
    # {{{

    CHUNK_LOSS_PERIOD = 10

    def __init__(self, peer):
        # {{{

        _p_("Initialized")

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
