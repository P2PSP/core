#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

from peer_dbs import Peer_DBS

import struct
import sys
import socket
from color import Color
from _print_ import _print_
import threading
import hashlib
import random

class TrustedPeer(Peer_DBS):

    PASS_NUMBER = 40
    SAMPLING_EFFORT = 1

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
        self.next_sampled_index = 0
        self.counter = 1

        # }}}
    def print_the_module_name(self):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Trusted Peer")
        sys.stdout.write(Color.none)

        # }}}

    def process_next_message(self):
        chunk_number = Peer_DBS.process_next_message(self)
        if chunk_number > 0 and self.current_sender != self.splitter:
            if self.counter == 0:
                self.send_chunk_hash(chunk_number)
                self.counter = self.calculate_next_sampled()
            else:
                self.counter -= 1
        return chunk_number

    def receive_the_next_message(self):
        message, sender = Peer_DBS.receive_the_next_message(self)
        self.current_sender = sender
        return message, sender

    def send_chunk_hash(self, chunk_number):
        chunk = self.chunks[chunk_number % self.buffer_size]
        chunk_hash = hashlib.sha256(chunk).digest()
        msg = struct.pack('H32s', chunk_number, chunk_hash)
        self.team_socket.sendto(msg, self.splitter)

    def calculate_next_sampled(self):
        max_random = len(self.peer_list) / TrustedPeer.SAMPLING_EFFORT
        return random.randint(1, max(1, max_random)) + TrustedPeer.PASS_NUMBER
