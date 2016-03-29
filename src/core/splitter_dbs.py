"""
@package core
splitter_dbs module
"""

# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# DBS: Data Broadcasting Set of rules

# {{{ Imports

#from __future__ import print_function
import threading
import sys
import socket
import struct
import time

<<<<<<< HEAD
from . import common
=======
from core.common import Common
>>>>>>> master
from core._print_ import _print_
from core.splitter_ims import Splitter_IMS
from core.color import Color

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
    
class Splitter_DBS(Splitter_IMS):
    # {{{

    # {{{ Class "constants"

    MAX_CHUNK_LOSS = 32     # Chunk losses threshold to reject a peer from the team.
    MCAST_ADDR = "0.0.0.0"
    MONITOR_NUMBER = 1
    
    # }}}

    def __init__(self):
        # {{{

        Splitter_IMS.__init__(self) #???
        #sys.stdout.write(Color.yellow)
        #print("Using DBS")
        #sys.stdout.write(Color.none)

        #self.number_of_monitors = 0
        self.peer_number = 0

        # {{{ The list of peers in the team.
        # }}}
        self.peer_list = []

        # }}}

        # {{{ Destination peers of the chunk, indexed by a chunk
        # number. Used to find the peer to which a chunk has been
        # sent.
        # }}}
        self.destination_of_chunk = [('0.0.0.0',0)] * self.BUFFER_SIZE
        #for i in range(self.BUFFER_SIZE):
        #    self.destination_of_chunk.append(('0.0.0.0',0))

        self.losses = {}
        self.magic_flags = Common.DBS
        
        _p_("max_chunk_loss =", self.MAX_CHUNK_LOSS)
        _p_("mcast_addr =", self.MCAST_ADDR)
        _p_("Initialized")

        # }}}

        #def say_goodbye(self, node, sock):
        # {{{

        #sock.sendto(b'', node)

        # }}}

    def send_magic_flags(self, peer_serve_socket):

        message = struct.pack("B", self.magic_flags)
        peer_serve_socket.sendall(message)
        _print_("Magic flags =",bin(self.magic_flags))
            
    def send_the_list_size(self, peer_serve_socket):
        # {{{

        _p_("Sending the number of monitors", self.MONITOR_NUMBER)
        message = struct.pack("H", socket.htons(self.MONITOR_NUMBER))
        peer_serve_socket.sendall(message)
        _p_("Sending a list of peers of size", len(self.peer_list))
        message = struct.pack("H", socket.htons(len(self.peer_list)))
        peer_serve_socket.sendall(message)

        # }}}

    def send_the_list_of_peers(self, peer_serve_socket):
        # {{{

        #if __debug__:
        #    print("Sending a list of peers of size", len(self.peer_list))
        #message = struct.pack("H", socket.htons(len(self.peer_list)))
        #peer_serve_socket.sendall(message)
        self.send_the_list_size(peer_serve_socket)

        #peer_serve_socket.sendall(self.message)

        if __debug__:
            counter = 0
        for p in self.peer_list:
            message = struct.pack("4sH", socket.inet_aton(p[ADDR]), \
                                  socket.htons(p[PORT]))
            peer_serve_socket.sendall(message)
            if __debug__:
                _p_("[%5d]" % counter, p)
                counter += 1

        # }}}

    # def append_peer_borrame(self, peer):
    #     # {{{

    #     if peer not in self.peer_list:
    #         self.peer_list.append(peer)
    #     self.losses[peer] = 0

    #     print("DBS: ---------------------------------")

        # }}}

    def send_the_peer_endpoint(self, peer_serve_socket):
        # {{{

        peer_endpoint = peer_serve_socket.getpeername()
        message = struct.pack("4sH", socket.inet_aton(peer_endpoint[ADDR]), \
                              socket.htons(peer_endpoint[PORT]))
        peer_serve_socket.sendall(message)

        # }}}

    # Pensar en reutilizar Splitter_IMS.handle_peer_arrival()
    # concatenando las llamadas a las funciones.

    def send_configuration(self, sock):
        Splitter_IMS.send_configuration(self, sock)
        self.send_the_peer_endpoint(sock)
        self.send_magic_flags(sock)

    def insert_peer(self, peer):
        # {{{

        if peer not in self.peer_list: # Probar a quitar -----------------------------------------------------
            #self.peer_list.insert(self.peer_number, peer)
            self.peer_list.append(peer)
        self.losses[peer] = 0

        _p_("inserted peer", peer)

        # }}}

    def handle_a_peer_arrival(self, connection):
        # {{{

        # {{{ In the DBS, the splitter sends to the incomming peer the
        # list of peers. Notice that the transmission of the list of
        # peers (something that could need some time if the team is
        # big or if the peer is slow) is done in a separate thread. This
        # helps to avoid DoS (Denial of Service) attacks.
        # }}}

        serve_socket = connection[0]
        incomming_peer = connection[1]
        #sys.stdout.write(Color.green)
        #print(serve_socket.getsockname(), '\b: DBS: accepted connection from peer', \
        #      incomming_peer)
        _p_('accepted connection from peer', incomming_peer)
        #sys.stdout.write(Color.none)
        self.send_configuration(serve_socket)
        self.send_the_list_of_peers(serve_socket)
        serve_socket.close()
        self.insert_peer(incomming_peer)
        return incomming_peer

        # }}}

    def receive_message(self):
        # {{{

        try:
            return self.team_socket.recvfrom(struct.calcsize("H"))
        except:
            _p_("Unexpected error:", sys.exc_info()[0])
            pass

        # }}}

    def get_lost_chunk_number(self, message):
        # {{{

        return struct.unpack("!H",message)[0]

        # }}}

    def get_losser(self, lost_chunk_number):
        # {{{

        return self.destination_of_chunk[lost_chunk_number % self.BUFFER_SIZE]

        # }}}

    def remove_peer(self, peer):
        # {{{

        try:
            self.peer_list.remove(peer)
        except ValueError:
            pass
        else:
            self.peer_number -= 1

        try:
            del self.losses[peer]
        except KeyError:
            pass

        # }}}

    def increment_unsupportivity_of_peer(self, peer):
        # {{{

        try:
            self.losses[peer] += 1
        except KeyError:
            _p_("the unsupportive peer", peer, "does not exist!")
        else:
            #sys.stdout.write(Color.blue)
            _p_(peer, "has loss", self.losses[peer], "chunks")
            #sys.stdout.write(Color.none)
            if self.losses[peer] > self.MAX_CHUNK_LOSS:
                if peer not in self.peer_list[:self.MONITOR_NUMBER]:
                    #sys.stdout.write(Color.red)
                    _p_(peer, 'removed')
                    self.remove_peer(peer)
                    #sys.stdout.write(Color.none)
        finally:
           pass

        # }}}

    def process_lost_chunk(self, lost_chunk_number, sender):
        # {{{

        destination = self.get_losser(lost_chunk_number)

        if __debug__:

            #sys.stdout.write(Color.cyan)
            _p_(sender, "complains about lost chunk", lost_chunk_number, "sent to", destination)
            #sys.stdout.write(Color.none)

            if destination in self.peer_list[:self.MONITOR_NUMBER]:
                _p_("lost chunk index =", lost_chunk_number)

        self.increment_unsupportivity_of_peer(destination)

        # }}}

    def process_goodbye(self, peer):
        # {{{

        #sys.stdout.write(Color.green)
        _p_('Received "goodbye" from', peer)
        #sys.stdout.write(Color.none)
        sys.stdout.flush()

        #if peer not in self.peer_list[:self.MONITOR_NUMBER]:
        self.remove_peer(peer)

        # }}}

    def moderate_the_team(self):
        # {{{

        while self.alive:
            # {{{

            message, sender = self.receive_message()

            if len(message) == 2:

                # {{{ The peer complains about a lost chunk.

                # In this situation, the splitter counts the number of
                # complains. If this number exceeds a threshold, the
                # unsupportive peer is expelled from the
                # team.

                lost_chunk_number = self.get_lost_chunk_number(message)
                self.process_lost_chunk(lost_chunk_number, sender)

                # }}}

            else:

                # {{{ The peer wants to leave the team.

                # A !2-length payload means that the peer wants to go
                # away.

                self.process_goodbye(sender)

                # }}}

            # }}}

        # }}}


    def setup_team_socket(self):
        # {{{

        # "team_socket" is used to talk to the peers of the team.
        self.team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # This does not work in Windows systems !!
        self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.team_socket.settimeout(1000.0)
        self.team_socket.bind(('', self.PORT))

        # }}}

    def reset_counters(self):
        # {{{

        for i in self.losses:
            self.losses[i] /= 2

        # }}}

    def reset_counters_thread(self):
        # {{{

        while self.alive:
            self.reset_counters()
            time.sleep(Common.COUNTERS_TIMING)

        # }}}

    def compute_next_peer_number(self, peer):
        # {{{ 

        self.peer_number = (self.peer_number + 1) % len(self.peer_list)

        # }}}

    def run(self):
        # {{{

        self.receive_the_header()

        # {{{ A DBS splitter runs 4 threads. The main one and the
        # "handle_arrivals" thread are equivalent to the daemons used
        # by the IMS splitter. "moderate_the_team" and
        # "reset_counters_thread" are new.
        # }}}

        _p_(self.peer_connection_socket.getsockname(), "\b: waiting for the monitor peers ...")
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
                self.chunk_number = (self.chunk_number + 1) % Common.MAX_CHUNK_NUMBER
                self.compute_next_peer_number(peer)
            except IndexError:
                _p_("The monitor peer has died!")


        # }}}

    # }}}
