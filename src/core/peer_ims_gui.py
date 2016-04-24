"""
@package core
peer_ims_gui module
"""

# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# IMS: Ip Multicasting Set of rules

# {{{ Imports

from __future__ import print_function
import threading
import sys
import socket
import struct
import time
from gi.repository import GObject

from core.common import Common
#from color import Color
from _print_ import _print_

try:
    from gui.adapter import buffering_adapter
except ImportError as msg:
    pass

# }}}

def _p_(*args, **kwargs):
    """Colorize the output."""
    sys.stdout.write(Common.IMS_COLOR)
    _print_("IMS:", *args)
    sys.stdout.write(Color.none)

class Peer_IMS_GUI(Peer_IMS):
    # {{{

    # {{{ Class "constants"

    BUFFER_STATUS = int(0)

    # }}}

    def buffer_data(self):
        # {{{ Buffering

        # {{{ The peer dies if the player disconnects.
        # }}}
        self.player_alive = True

        # {{{ The last chunk sent to the player.
        # }}}
        self.played_chunk = 0

        # {{{ Counts the number of executions of the recvfrom()
        # function.
        # }}}
        self.recvfrom_counter = 0

        # {{{ Label the chunks in the buffer as "received" or "not
        # received".
        # }}}
        self.received_flag = []

        # {{{ The buffer of chunks is a structure that is used to delay
        # the playback of the chunks in order to accommodate the
        # network jittter. Two components are needed: (1) the "chunks"
        # buffer that stores the received chunks and (2) the
        # "received" buffer that stores if a chunk has been received
        # or not. Notice that each peer can use a different
        # buffer_size: the smaller the buffer size, the lower start-up
        # time, the higher chunk-loss ratio. However, for the sake of
        # simpliticy, all peers will use the same buffer size.

        self.chunks = [""]*self.buffer_size
        self.received_flag = [False]*self.buffer_size
        self.received_counter = 0

        # }}}

        #  Wall time (execution time plus waiting time).
        start_time = time.time()

        # We will send a chunk to the player when a new chunk is
        # received. Besides, those slots in the buffer that have not been
        # filled by a new chunk will not be send to the player. Moreover,
        # chunks can be delayed an unknown time. This means that (due to the
        # jitter) after chunk X, the chunk X+Y can be received (instead of the
        # chunk X+1). Alike, the chunk X-Y could follow the chunk X. Because
        # we implement the buffer as a circular queue, in order to minimize
        # the probability of a delayed chunk overwrites a new chunk that is
        # waiting for traveling the player, we wil fill only the half of the
        # circular queue.

        _p_(self.team_socket.getsockname(), "\b: buffering = 000.00%")
        sys.stdout.flush()

        # First chunk to be sent to the player.  The
        # process_next_message() procedure returns the chunk number if
        # a packet has been received or -2 if a time-out exception has
        # been arised.
        chunk_number = self.process_next_message()
        while chunk_number < 0:
            chunk_number = self.process_next_message()
            _p_(chunk_number)
        self.played_chunk = chunk_number
        _p_("First chunk to play", self.played_chunk)
        _p_(self.team_socket.getsockname(), "\b: buffering (\b", repr(100.0/self.buffer_size).rjust(4))

        # Now, fill up to the half of the buffer.
        for x in range(int(self.buffer_size/2)):
            _print_("{:.2%}\r".format((1.0*x)/(self.buffer_size/2)), end='')
<<<<<<< HEAD
            BUFFER_STATUS = int((100*x)/(self.buffer_size/2)+1)
            if common.CONSOLE_MODE == False :
                _print_(str(BUFFER_STATUS))
=======
            BUFFER_STATUS = (100*x)/(self.buffer_size/2) +1
            if Common.CONSOLE_MODE == False :
>>>>>>> master
                GObject.idle_add(buffering_adapter.update_widget,BUFFER_STATUS)
            else:
                pass
            #print("!", end='')
            sys.stdout.flush()
            while self.process_next_message() < 0:
                pass

        print()
        latency = time.time() - start_time
        _p_('latency =', latency, 'seconds')
        _p_("buffering done.")
        sys.stdout.flush()

        # }}}

    # }}}
