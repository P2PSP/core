#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

from peer_dbs import Peer_DBS
from _print_ import _print_
from color import Color
import struct

class Peer_StrpeDs(Peer_DBS):

    def __init__(self):
        sys.stdout.write(Color.yellow)
        _print_("STrPe-DS Peer")
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
        self.message_format += '40s40s'

    def process_message(self, message, sender):
        # here hash checking will be implemented
        return Peer_DBS.process_message(self, message, sender)

    def unpack_message(self, message):
        # {{{

        chunk_number, chunk, k1, k2 = struct.unpack(self.message_format, message)
        chunk_number = socket.ntohs(chunk_number)

        return chunk_number, chunk

        # }}}
