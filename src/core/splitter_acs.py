"""
@package core
splitter_ace module
"""

# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# ACS: Adaptive Chunk-rate Set of rules

# {{{ Imports

from __future__ import print_function
import threading
import sys
import socket
import struct
import time

<<<<<<< HEAD
from . import common
#from core.color import Color
=======
from core.common import Common
from core.color import Color
>>>>>>> master
from core._print_ import _print_
#from splitter_ims import Splitter_IMS
from core.splitter_dbs import Splitter_DBS
#from splitter_fns import Splitter_FNS

# }}}

def _p_(*args, **kwargs):
    """Colorize the output."""
    if __debug__:
        sys.stdout.write(Common.ACS_COLOR)
        _print_("ACS:", *args)
        sys.stdout.write(Color.none)

class Splitter_ACS(Splitter_DBS):
    # {{{
    
    def __init__(self, splitter):
        # {{{

        #Splitter_FNS.__init__(self)
        #sys.stdout.write(Color.yellow)
        #print("Using ACS")
        #sys.stdout.write(Color.none)

        self.period = {}                         # Indexed by a peer (IP address, port)
        self.period_counter = {}                 # Indexed by a peer (IP address, port)
        self.number_of_sent_chunks_per_peer = {} # Indexed by a peer (IP address, port)

        self.magic_flags |= Common.ACS
        
        _p_("Initialized")
        
        # }}}

    def insert_peer(self, peer):
        # {{{

        Splitter_DBS.insert_peer(self, peer)
        self.period[peer] = self.period_counter[peer] = 1
        self.number_of_sent_chunks_per_peer[peer] = 0
        #if __debug__:
        _p_("inserted", peer)

        # }}}

    def increment_unsupportivity_of_peer(self, peer):
        # {{{

        Splitter_DBS.increment_unsupportivity_of_peer(self, peer)
        try:
            if peer != self.peer_list[0]:
                self.period[peer] += 1
                self.period_counter[peer] = self.period[peer]
        except KeyError:
            pass

        # }}}

    def remove_peer(self, peer):
        # {{{

        Splitter_DBS.remove_peer(self, peer)
        try:
            del self.period[peer]
        except KeyError:
            pass

        try:
            del self.period_counter[peer]
        except KeyError:
            pass

        try:
            del self.number_of_sent_chunks_per_peer[peer]
        except KeyError:
            pass

        # }}}

    def reset_counters(self):
        # {{{

        Splitter_DBS.reset_counters(self)
        for i in self.period:
            #self.period[i] = ( self.period[i] + 1 ) / 2
            self.period[i] -= 1
            if self.period[i] < 1:
                self.period[i] = 1
            #self.period_counter[i] = self.period[i]

        # }}}

    def send_chunk(self, chunk, peer):
        # {{{

        Splitter_DBS.send_chunk(self, chunk, peer)
        try:
            self.number_of_sent_chunks_per_peer[peer] += 1
        except KeyError:
            pass

        # }}}

    def compute_next_peer_number(self, peer):
        # {{{

        try:
            while self.period_counter[peer] != 0:
                self.period_counter[peer] -= 1
                self.peer_number = (self.peer_number + 1) % len(self.peer_list)
                peer = self.peer_list[self.peer_number]
            self.period_counter[peer] = self.period[peer] # ojo, inservible?
        except KeyError:
            pass

        # }}}

    # }}}
