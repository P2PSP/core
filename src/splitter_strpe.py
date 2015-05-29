#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

import struct
import sys
import binascii
from color import Color
from _print_ import _print_

from splitter_lrs import Splitter_LRS

class StrpeSplitter(Splitter_LRS):

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
            elif len(message) == 8:
                # trusted peer sends hash of received chunk
                # number of chunk, hash (crc32) of chunk
                #if sender in self.trusted_peers:
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
        chunk_number, hash = struct.unpack('Hi', message)
        chunk_message = self.buffer[chunk_number % self.BUFFER_SIZE]
        chunk = struct.unpack(self.get_message_format(), chunk_message)[1]
        if binascii.crc32(chunk) != hash:
            peer = self.destination_of_chunk[chunk_number % self.BUFFER_SIZE]
            self.punish_malicious_peer(peer)

    def get_message_format(self):
        return self.chunk_number_format + str(self.CHUNK_SIZE) + "s"

    def punish_malicious_peer(self, peer):
        print('!!! malicous peer ' + str(peer))
        self.remove_peer(peer)

    def add_trusted_peer(self, peer):
        self.trusted_peers.append(peer)

    def receive_message(self):
        # {{{

        try:
            return self.team_socket.recvfrom(struct.calcsize("Hi"))
        except:
            if __debug__:
                print("DBS: Unexpected error:", sys.exc_info()[0])
            pass

        # }}}
