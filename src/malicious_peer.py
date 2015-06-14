#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

import struct
import socket
import sys
import threading

from color import Color
from _print_ import _print_
from peer_dbs import Peer_DBS
from malicious_socket import MaliciousSocket

ADDR = 0
PORT = 1

class MaliciousPeer(Peer_DBS):

    def __init__(self, peer):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Malicious Peer")
        sys.stdout.write(Color.none)

        threading.Thread.__init__(self)

        self.splitter_socket = peer.splitter_socket
        self.player_socket = peer.player_socket
        self.buffer_size = peer.buffer_size
        self.splitter = peer.splitter
        self.chunk_size = peer.chunk_size
        self.message_format = peer.message_format

        # }}}

    def print_the_module_name(self):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Malicious Peer")
        sys.stdout.write(Color.none)

        # }}}

    def listen_to_the_team(self):
        # {{{ Create "team_socket" (UDP) as a copy of "splitter_socket" (TCP)

        self.team_socket = MaliciousSocket(self.message_format, socket.AF_INET, socket.SOCK_DGRAM)
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
