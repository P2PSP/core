"""
@package core
peer_dbs module
"""

# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# DBS: Data Broadcasting Set of rules

# {{{

from __future__ import print_function
import threading
import sys
import socket
import struct
import time

from core.common import Common

from core.color import Color
from core._print_ import _print_
#from core.peer_ims import Peer_IMS
from core.peer_ims_gui import Peer_IMS_GUI as Peer_IMS

# }}}

# Some useful definitions.
ADDR = 0
PORT = 1

def _p_(*args, **kwargs):
    """Colorize the output."""
    if __debug__:
        sys.stdout.write(Common.DBS_COLOR)
        _print_("DBS:", *args)
        sys.stdout.write(Color.none)

class Peer_DBS(Peer_IMS):
    # {{{

    # {{{ Class "constants"

    MAX_CHUNK_DEBT = 128 # Peer's rejecting threshold

    LOGGING = False # A IMS???
    LOG_FILE = ""   # A IMS???

    # }}}

    def __init__(self, peer):
        # {{{

        _p_("max_chunk_debt =", self.MAX_CHUNK_DEBT)
        _p_("Initialized")

        # }}}

    def say_hello(self, node):
        # {{{

        self.team_socket.sendto(b'H', node)
        _p_("[Hello] sent to %s" % str(node))

        # }}}

    def say_goodbye(self, node):
        # {{{

        self.team_socket.sendto(b'G', node)
        _p_("[Goodbye] sent to %s" % str(node))

        # }}}

    def receive_magic_flags(self):
        self.magic_flags = struct.unpack("B",self.splitter_socket.recv(struct.calcsize("B")))[0]
        _p_("Magic flags =", bin(self.magic_flags))

    def receive_the_number_of_peers(self):
        # {{{

        self.debt = {}      # Chunks debts per peer.
        self.peer_list = [] # The list of peers structure.

        #sys.stdout.write(Color.green)
        _p_("Requesting the number of monitors and peers to", self.splitter_socket.getpeername())
        self.number_of_monitors = socket.ntohs(struct.unpack("H",self.splitter_socket.recv(struct.calcsize("H")))[0])
        _p_("The number of monitors is", self.number_of_monitors)
        self.number_of_peers = socket.ntohs(struct.unpack("H",self.splitter_socket.recv(struct.calcsize("H")))[0])
        _p_("The size of the team is", self.number_of_peers, "(apart from me)")

        #sys.stdout.write(Color.none)

        # }}}

    def receive_the_list_of_peers(self):
        # {{{

        self.debt = {}      # Chunks debts per peer.
        self.peer_list = [] # The list of peers structure.

        #sys.stdout.write(Color.green)
        _p_("Requesting", self.number_of_peers, "peers to", self.splitter_socket.getpeername())
        #number_of_peers = socket.ntohs(struct.unpack("H",self.splitter_socket.recv(struct.calcsize("H")))[0])
        #_print_("The size of the team is", number_of_peers, "(apart from me)")

        tmp = self.number_of_peers
        while tmp > 0:
            message = self.splitter_socket.recv(struct.calcsize("4sH"))
            IP_addr, port = struct.unpack("4sH", message) # Ojo, !H ????
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            peer = (IP_addr, port)
            _p_("[hello] sent to", peer)
            self.say_hello(peer)
            if __debug__:
                _p_("[%5d]" % tmp, peer)
            else:
                _print_("{:.2%}\r".format((self.number_of_peers-tmp)/self.number_of_peers), end='')

            self.peer_list.append(peer)
            self.debt[peer] = 0
            tmp -= 1

        _p_("List of peers received")
        #sys.stdout.write(Color.none)

        # }}}

    def receive_my_endpoint(self):
        # {{{

        message = self.splitter_socket.recv(struct.calcsize("4sH"))
        IP_addr, port = struct.unpack("4sH", message) # Ojo, !H ????
        IP_addr = socket.inet_ntoa(IP_addr)
        port = socket.ntohs(port)
        self.me = (IP_addr, port)
        _p_("me =", self.me)

        # }}}

    def listen_to_the_team(self):
        # {{{ Create "team_socket" (UDP) as a copy of "splitter_socket" (TCP)

        self.create_team_socket()
        try:
            # In Windows systems this call doesn't work!
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception as e:
            print ("DBS:", e)
            pass
        self.team_socket.bind(('', self.splitter_socket.getsockname()[PORT]))

        # This is the maximum time the peer will wait for a chunk
        # (from the splitter or from another peer).
        self.team_socket.settimeout(1)

        # }}}

    def process_message(self, message, sender):
        # {{{ Now, receive and send.

        if len(message) == struct.calcsize(self.message_format):
            # {{{ A video chunk has been received

            chunk_number, chunk = self.unpack_message(message)
            self.chunks[chunk_number % self.buffer_size] = chunk
            self.received_flag[chunk_number % self.buffer_size] = True
            self.received_counter += 1

            if sender == self.splitter:
                # {{{ Send the previous chunk in burst sending
                # mode if the chunk has not been sent to all
                # the peers of the list of peers.

                # {{{ debug

                _p_(self.team_socket.getsockname(), "<-", chunk_number, "-", sender)
                if __debug__: # No aqui. Tal vez, DIS

                    if self.LOGGING:
                        self.log_message("buffer correctnes {0}".format(self.calc_buffer_correctnes()))
                        self.log_message("buffer filling {0}".format(self.calc_buffer_filling()))

                # }}}

                while( (self.receive_and_feed_counter < len(self.peer_list)) and (self.receive_and_feed_counter > 0) ):
                    peer = self.peer_list[self.receive_and_feed_counter]
                    self.team_socket.sendto(self.receive_and_feed_previous, peer)
                    self.sendto_counter += 1

                    _p_(self.team_socket.getsockname(), "-",\
                        socket.ntohs(struct.unpack(self.message_format, \
                                                   self.receive_and_feed_previous)[0]),\
                        "->", peer)

                    self.debt[peer] += 1
                    if self.debt[peer] > self.MAX_CHUNK_DEBT:
                        _p_(peer, 'removed by unsupportive (' + str(self.debt[peer]) + ' lossess)')
                        del self.debt[peer]
                        self.peer_list.remove(peer)

                    self.receive_and_feed_counter += 1

                self.receive_and_feed_counter = 0
                self.receive_and_feed_previous = message

               # }}}
            else:
                # {{{ The sender is a peer

                _p_(self.team_socket.getsockname(), \
                    "<-", chunk_number, "-", sender)

                if sender not in self.peer_list:
                    # The peer is new
                    self.peer_list.append(sender)
                    self.debt[sender] = 0
                    _p_(sender, 'added by chunk', chunk_number)
                else:
                    self.debt[sender] -= 1

                # }}}

            # {{{ A new chunk has arrived and the
            # previous must be forwarded to next peer of the
            # list of peers.
            if ( self.receive_and_feed_counter < len(self.peer_list) and ( self.receive_and_feed_previous != '') ):
                # {{{ Send the previous chunk in congestion avoiding mode.

                peer = self.peer_list[self.receive_and_feed_counter]
                self.team_socket.sendto(self.receive_and_feed_previous, peer)
                self.sendto_counter += 1

                self.debt[peer] += 1
                if self.debt[peer] > self.MAX_CHUNK_DEBT:
                    _p_(peer, 'removed by unsupportive (' + str(self.debt[peer]) + ' lossess)')
                    del self.debt[peer]
                    self.peer_list.remove(peer)

                _p_(self.team_socket.getsockname(), "-", \
                    socket.ntohs(struct.unpack(self.message_format, self.receive_and_feed_previous)[0]),\
                    "->", peer)

                self.receive_and_feed_counter += 1

                # }}}
            # }}}

            return chunk_number

            # }}}
        else:
            # {{{ A control chunk has been received
            _p_("Control message received")
            if message == 'H':
                if sender not in self.peer_list:
                    # The peer is new
                    self.peer_list.append(sender)
                    self.debt[sender] = 0
                    _p_(sender, 'added by [hello]')
            else:
                if sender in self.peer_list:
                    #sys.stdout.write(Color.red)
                    _p_(self.team_socket.getsockname(), '\b: received "goodbye" from', sender)
                    #sys.stdout.write(Color.none)
                    self.peer_list.remove(sender)
                    del self.debt[sender]
            return -1

            # }}}

        # }}}

    def keep_the_buffer_full(self):
        # {{{

        Peer_IMS.keep_the_buffer_full(self)
        if (self.played_chunk % self.debt_memory) == 0:
            for i in self.debt:
                self.debt[i] /= 2

        #_p_("Number of peers in the team:", len(self.peer_list)+1)
        #_p_(self.team_socket.getsockname(),)
        #if __debug__:
        #    for p in self.peer_list:
        #        print ("DBS:", p,)
        #    print ()

        # }}}

    def polite_farewell(self):
        # {{{

        _p_('Goodbye!')
        for x in range(3):
            self.process_next_message()
            self.say_goodbye(self.splitter)
        for peer in self.peer_list:
            self.say_goodbye(peer)

        # }}}

    def buffer_data(self):
        # {{{

        # Number of times that the previous received chunk has been sent
        # to the team. If this counter is smaller than the number
        # of peers in the team, the previous chunk must be sent in the
        # burst mode because a new chunk from the splitter has arrived
        # and the previous received chunk has not been sent to all the
        # peers of the team. This can happen when one or more chunks
        # that were routed towards this peer have been lost.
        self.receive_and_feed_counter = 0

        # This "private and static" variable holds the previous chunk
        # received from the splitter. It is used to send the previous
        # received chunk in the congestion avoiding mode. In that
        # mode, the peer sends a chunk only when it received a chunk
        # from another peer or from the splitter.
        self.receive_and_feed_previous = ""

        self.sendto_counter = 0

        self.debt_memory = 1 << self.MAX_CHUNK_DEBT

        Peer_IMS.buffer_data(self)

        # }}}

    def run(self):
        # {{{

        #Peer_IMS.peers_life(self)
        Peer_IMS.run(self)
        self.polite_farewell()

        # }}}

    def am_i_a_monitor(self):
        # {{{
        if self.number_of_peers < self.number_of_monitors:
            # Only the first peers of the team are monitor peers
            return True
        else:
            return False
        #message = self.splitter_socket.recv(struct.calcsize("c"))
        #if struct.unpack("c", message)[0] == '1':
        #    return True
        #else:
        #    return False

        # }}}

    # }}}

    # The following methods should be inheritaged ... in DIS??

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

    def calc_buffer_filling(self):
        chunks = 0
        for i in range(self.buffer_size):
            if self.received_flag[i]:
                chunks += 1
        return chunks / float(self.buffer_size)

    def log_message(self, message):
        self.LOG_FILE.write(self.build_log_message(message) + "\n")
        #print >>self.LOG_FILE, self.build_log_message(message)

    def build_log_message(self, message):
        return "{0}\t{1}".format(repr(time.time()), message)
