"""
@package core
peer_strpeds module
"""

# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

from __future__ import print_function
import threading
import sys
import socket
import struct
import time
#import traceback

<<<<<<< HEAD
from . import common
=======
from core.common import Common
>>>>>>> master
from core.color import Color
from core._print_ import _print_
#from peer_ims import Peer_IMS
#from peer_dbs import Peer_DBS
<<<<<<< HEAD
from core.peer_nts import Peer_NTS
=======
from core.peer_dbs import Peer_DBS
>>>>>>> master
try:
    from Crypto.PublicKey import DSA
    from Crypto.Hash import SHA256
except ImportError:
    pass
#except Exception as msg:
#    traceback.print_exc()

# Some useful definitions.
ADDR = 0
PORT = 1

def _p_(*args, **kwargs):
    """Colorize the output."""
    sys.stdout.write(Common.DIS)
    _print_("DIS (STRPEDS):", *args)
    sys.stdout.write(Color.none)

class Peer_StrpeDs(Peer_DBS):

    def __init__(self, peer):

        self.message_format += '40s40s'
        self.bad_peers = []

        _p_("Initialized")

    def process_message(self, message, sender):
        if sender in self.bad_peers:
            return -1

        if self.is_current_message_from_splitter() or self.check_message(message, sender):
            if self.is_control_message(message) and message == 'B':
                return self.handle_bad_peers_request()
            else:
                return Peer_DBS.process_message(self, message, sender)
        else:
            self.process_bad_message(message, sender)
            return -1

    def handle_bad_peers_request(self):
        msg = struct.pack("3sH", "bad", len(self.bad_peers))
        self.team_socket.sendto(msg, self.splitter)
        for peer in self.bad_peers:
            ip = struct.unpack("!L", socket.inet_aton(peer[0]))[0]
            msg = struct.pack('ii', ip, peer[1])
            self.team_socket.sendto(msg, self.splitter)
        return -1

    def check_message(self, message, sender):
        if sender in self.bad_peers:
            return False
        if not self.is_control_message(message):
            chunk_number, chunk, k1, k2 = struct.unpack(self.message_format, message)
            chunk_number = socket.ntohs(chunk_number)
            sign = (self.convert_to_long(k1), self.convert_to_long(k2))
            m = str(chunk_number) + str(chunk) + str(sender)
            return self.dsa_key.verify(SHA256.new(m).digest(), sign)
        return True

    def is_control_message(self, message):
        return len(message) != struct.calcsize(self.message_format)

    def process_bad_message(self, message, sender):
        _print_("bad peer: " + str(sender))
        self.bad_peers.append(sender)
        self.peer_list.remove(sender)

    def unpack_message(self, message):
        # {{{
        chunk_number, chunk, k1, k2 = struct.unpack(self.message_format, message)
        chunk_number = socket.ntohs(chunk_number)
        return chunk_number, chunk
        # }}}

    def receive_dsa_key(self):
        message = self.splitter_socket.recv(struct.calcsize("256s256s256s40s"))
        y, g, p, q = struct.unpack("256s256s256s40s", message)
        y = self.convert_to_long(y)
        g = self.convert_to_long(g)
        p = self.convert_to_long(p)
        q = self.convert_to_long(q)
        self.dsa_key = DSA.construct((y, g, p, q))
        _print_("DSA key received")

    def convert_to_long(self, s):
        return long(s.rstrip('\x00'), 16)

    def receive_the_next_message(self):
        message, sender = Peer_DBS.receive_the_next_message(self)
        self.current_sender = sender
        return message, sender

    def is_current_message_from_splitter(self):
        return self.current_sender == self.splitter
