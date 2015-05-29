#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

from peer_dbs import Peer_DBS

import struct
import binascii
import sys
import socket
from color import Color
from _print_ import _print_
import threading

class TrustedPeer(Peer_DBS):

    def __init__(self, peer):
        sys.stdout.write(Color.yellow)
        _print_("Trusted Peer")
        sys.stdout.write(Color.none)

        threading.Thread.__init__(self)

        self.splitter_socket = peer.splitter_socket
        self.player_socket = peer.player_socket
        self.buffer_size = peer.buffer_size
        self.splitter = peer.splitter
        self.chunk_size = peer.chunk_size
        self.peer_list = peer.peer_list
        self.debt = peer.debt
        self.message_format = peer.message_format
        self.team_socket = peer.team_socket

        self.counter = 0

        # }}}
    def print_the_module_name(self):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Trusted Peer")
        sys.stdout.write(Color.none)

        # }}}

    def process_next_message(self):
        chunk_number = Peer_DBS.process_next_message(self)
        if chunk_number > 0 and self.counter % 255 == 0:
            chunk = self.chunks[chunk_number % self.buffer_size]
            msg = struct.pack('Hi', chunk_number, binascii.crc32(chunk))
            self.team_socket.sendto(msg, self.splitter)
        self.counter += 1
        return chunk_number
