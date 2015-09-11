#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

import struct
import sys
import hashlib
import time
from color import Color
from _print_ import _print_
import threading
import socket
import common

from splitter_lrs import Splitter_LRS

class StrpeSplitter(Splitter_LRS):

    LOGGING = False
    LOG_FILE = ""
    CURRENT_ROUND = 0

    def __init__(self):
        sys.stdout.write(Color.yellow)
        print("STrPe")
        sys.stdout.write(Color.none)
        Splitter_LRS.__init__(self)
        self.trusted_peers = []

    def moderate_the_team(self):
        while self.alive:
            # {{{

            try:
                message, sender = self.receive_message()
            except:
                message = b'?'
                sender = ("0.0.0.0", 0)
            if len(message) == 2:

                # {{{ The peer complains about a lost chunk.

                # In this situation, the splitter counts the number of
                # complains. If this number exceeds a threshold, the
                # unsupportive peer is expelled from the
                # team.

                lost_chunk_number = self.get_lost_chunk_number(message)
                self.process_lost_chunk(lost_chunk_number, sender)

                # }}}
            elif len(message) == 34:
                # trusted peer sends hash of received chunk
                # number of chunk, hash (sha256) of chunk
                endpoint = sender[0] + ':' + str(sender[1])
                if endpoint in self.trusted_peers:
                    self.process_chunk_hash_message(message)
            else:
                # {{{ The peer wants to leave the team.

                try:
                    if struct.unpack("s", message)[0] == 'G': # 'G'oodbye
                        self.process_goodbye(sender)
                except Exception as e:
                    print("LRS: ", e)
                    print(message)
                # }}}
            # }}}

    def process_chunk_hash_message(self, message):
        chunk_number, hash = struct.unpack('H32s', message)
        chunk_message = self.buffer[chunk_number % self.BUFFER_SIZE]
        stored_chunk_number, chunk = struct.unpack(self.get_message_format(), chunk_message)
        stored_chunk_number = socket.ntohs(stored_chunk_number)
        if stored_chunk_number == chunk_number and hashlib.sha256(chunk).digest() != hash:
            peer = self.destination_of_chunk[chunk_number % self.BUFFER_SIZE]
            self.punish_malicious_peer(peer)

    def get_message_format(self):
        return self.chunk_number_format + str(self.CHUNK_SIZE) + "s"

    def punish_malicious_peer(self, peer):
        if self.LOGGING:
            self.log_message('!!! malicous peer ' + str(peer))
        print('!!! malicous peer ' + str(peer))
        self.remove_peer(peer)

    def add_trusted_peer(self, peer):
        self.trusted_peers.append(peer)

    def receive_message(self):
        # {{{

        try:
            return self.team_socket.recvfrom(struct.calcsize("H32s"))
        except:
            if __debug__:
                print("DBS: Unexpected error:", sys.exc_info()[0])
            pass

        # }}}

    def run(self):
        # {{{

        self.receive_the_header()

        # {{{ A DBS splitter runs 4 threads. The main one and the
        # "handle_arrivals" thread are equivalent to the daemons used
        # by the IMS splitter. "moderate_the_team" and
        # "reset_counters_thread" are new.
        # }}}

        print(self.peer_connection_socket.getsockname(), "\b: DBS: waiting for the monitor peer ...")
        def _():
            connection  = self.peer_connection_socket.accept()
            incomming_peer = self.handle_a_peer_arrival(connection)
            #self.insert_peer(incomming_peer) # Notice that now, the
                                             # monitor peer is the
                                             # only one in the list of
                                             # peers. It is no
                                             # neccesary a delay.
        _()

        threading.Thread(target=self.handle_arrivals).start()
        threading.Thread(target=self.moderate_the_team).start()
        threading.Thread(target=self.reset_counters_thread).start()

        message_format = self.chunk_number_format \
                        + str(self.CHUNK_SIZE) + "s"

        #header_load_counter = 0
        while self.alive:

            chunk = self.receive_chunk()
            try:
                peer = self.peer_list[self.peer_number]
                message = struct.pack(message_format, socket.htons(self.chunk_number), chunk)
                self.send_chunk(message, peer)

                self.destination_of_chunk[self.chunk_number % self.BUFFER_SIZE] = peer
                self.chunk_number = (self.chunk_number + 1) % common.MAX_CHUNK_NUMBER
                self.compute_next_peer_number(peer)
                if self.LOGGING:
                    if self.peer_number == 0:
                        self.CURRENT_ROUND += 1
                        message = "{0} {1} {2}".format(self.CURRENT_ROUND, len(self.peer_list), " ".join(map(lambda x: "{0}:{1}".format(x[0], x[1]), self.peer_list)))
                        self.log_message(message)

            except IndexError:
                if __debug__:
                    _print_("DBS: The monitor peer has died!")


        # }}}

    def log_message(self, message):
        print >>self.LOG_FILE, self.build_log_message(message)

    def build_log_message(self, message):
        return "{0}\t{1}".format(repr(time.time()), message)
