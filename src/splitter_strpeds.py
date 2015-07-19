#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org


import binascii
import struct
import sys
import threading
import socket
from color import Color
import common
from _print_ import _print_
from Crypto.Random import random
from Crypto.PublicKey import DSA
from Crypto.Hash import SHA256
from splitter_dbs import Splitter_DBS
from splitter_lrs import Splitter_LRS

class StrpeDsSplitter(Splitter_LRS):

    DIGEST_SIZE = 40

    def __init__(self):
        sys.stdout.write(Color.yellow)
        print("Using STrPe-DS")
        sys.stdout.write(Color.none)
        Splitter_LRS.__init__(self)
        self.trusted_peers = []

    def add_trusted_peer(self, peer):
        self.trusted_peers.append(peer)

    def handle_a_peer_arrival(self, connection):
        serve_socket = connection[0]
        incomming_peer = connection[1]
        sys.stdout.write(Color.green)
        print(serve_socket.getsockname(), '\b: DBS: accepted connection from peer', \
              incomming_peer)
        sys.stdout.write(Color.none)
        self.send_configuration(serve_socket)
        self.send_the_list_of_peers(serve_socket)
        self.send_dsa_key(serve_socket)
        self.insert_peer(incomming_peer)
        serve_socket.close()
        return incomming_peer

    def send_dsa_key(self, sock):
        # send Public key (y), Sub-group generator (g), Modulus, finite field order (p), Sub-group order (q)
        y = self.long_to_hex(self.dsa_key.y)
        g = self.long_to_hex(self.dsa_key.g)
        p = self.long_to_hex(self.dsa_key.p)
        q = self.long_to_hex(self.dsa_key.q)
        message = struct.pack('256s256s256s40s', y, g, p, q)
        sock.sendall(message)

    def run(self):
        # {{{

        self.receive_the_header()

        self.init_key()

        print(self.peer_connection_socket.getsockname(), "\b: STrPe-DS: waiting for the monitor peer ...")
        self.handle_a_peer_arrival(self.peer_connection_socket.accept())

        threading.Thread(target=self.handle_arrivals).start()
        threading.Thread(target=self.moderate_the_team).start()
        threading.Thread(target=self.reset_counters_thread).start()

        message_format = self.chunk_number_format \
                        + str(self.CHUNK_SIZE) + "s" \
                        + str(self.DIGEST_SIZE) + "s" \
                        + str(self.DIGEST_SIZE) + "s"

        while self.alive:

            chunk = self.receive_chunk()
            try:
                peer = self.peer_list[self.peer_number]
                message = self.get_message(self.chunk_number, chunk, peer)
                self.send_chunk(message, peer)

                self.destination_of_chunk[self.chunk_number % self.BUFFER_SIZE] = peer
                self.chunk_number = (self.chunk_number + 1) % common.MAX_CHUNK_NUMBER
                self.compute_next_peer_number(peer)
            except IndexError:
                if __debug__:
                    _print_("DBS: The monitor peer has died!")

        # }}}

    # }}}

    def init_key(self):
        self.dsa_key = DSA.generate(1024)
        _print_("DSA key generated")
        _print_("y = " + str(self.dsa_key.y))
        _print_("g = " + str(self.dsa_key.g))
        _print_("p = " + str(self.dsa_key.p))
        _print_("q = " + str(self.dsa_key.q))

    def get_message(self, chunk_number, chunk, dst):
        m = str(chunk_number) + str(chunk) + str(dst)
        h = SHA256.new(m).digest()
        k = random.StrongRandom().randint(1, self.dsa_key.q-1)
        sig = self.dsa_key.sign(h,k)
        return struct.pack('H1024s40s40s', socket.htons(chunk_number), chunk, self.long_to_hex(sig[0]), self.long_to_hex(sig[1]))

    def long_to_hex(self, value):
        return '%x' % value
