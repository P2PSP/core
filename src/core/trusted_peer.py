"""
@package core
malicious_peer module
"""

# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

<<<<<<< HEAD
from .peer_dbs import Peer_DBS

import struct
import sys
import socket
from core.color import Color
from core._print_ import _print_
=======
import struct
import sys
import socket
>>>>>>> master
import threading
import hashlib
import random
import time

from core.color import Color
from core._print_ import _print_
from core.peer_dbs import Peer_DBS

def _p_(*args, **kwargs):
    """Colorize the output."""
    sys.stdout.write(Common.DBS)
    _print_("DBS (trusted peer):", *args)
    sys.stdout.write(Color.none)

class TrustedPeer(Peer_DBS):

    PASS_NUMBER = 10
    SAMPLING_EFFORT = 2

    checkAll = False

    def __init__(self, peer):

        self.next_sampled_index = 0
        self.counter = 1
        _p_("Initialized")

    def process_next_message(self):
        chunk_number = Peer_DBS.process_next_message(self)
        if chunk_number > 0 and self.current_sender != self.splitter:
            if self.counter == 0:
                self.send_chunk_hash(chunk_number)
                self.counter = self.calculate_next_sampled()
            else:
                self.counter -= 1

        return chunk_number

    def calc_buffer_correctnes(self):
        zerochunk = struct.pack("1024s", "0")
        goodchunks = badchunks = 0
        for i in range(self.buffer_size):
            if self.received_flag[i]:
                if self.chunks[i] == zerochunk:
                    badchunks += 1
                else:
                    goodchunks += 1
        return goodchunks / float(goodchunks + badchunks)

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
        if self.checkAll:
            return 0
        max_random = len(self.peer_list) / TrustedPeer.SAMPLING_EFFORT
        return random.randint(0, max(1, max_random)) + TrustedPeer.PASS_NUMBER

    def setCheckAll(self, value):
        self.checkAll = value
