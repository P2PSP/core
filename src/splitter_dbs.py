# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucía
# through the Proyecto Motriz "Codificación de Vídeo Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

from __future__ import print_function
import threading
import sys
import socket
import struct
import time
from color import Color
import common
from _print_ import _print_
from splitter_ims import Splitter_IMS

# }}}

# Some useful definitions.
ADDR = 0
PORT = 1

# DBS: Data Broadcasting Set of rules
class Splitter_DBS(Splitter_IMS):
    # {{{

    # {{{ Class "constants"

    # {{{ Threshold of chunk losses to reject a peer from the team.
    # }}}
    MAX_CHUNK_LOSS = 32
    MCAST_ADDR = "0.0.0.0"

    # }}}

    def __init__(self):
        # {{{

        Splitter_IMS.__init__(self)
        sys.stdout.write(Color.yellow)
        print("Using DBS")
        sys.stdout.write(Color.none)

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

        print("DBS: max_chunk_loss =", self.MAX_CHUNK_LOSS)
        print("DBS: mcast_addr =", self.MCAST_ADDR)

        # }}}

    def say_goodbye(self, node, sock):
        # {{{

        sock.sendto(b'', node)

        # }}}

    def send_the_list_size(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("DBS: Sending a list of peers of size", len(self.peer_list))
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
                print("DBS: [%5d]" % counter, p)
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
        
    def insert_peer(self, peer):
        # {{{
        if peer not in self.peer_list: # Probar a quitar -----------------------------------------------------
            #self.peer_list.insert(self.peer_number, peer)
            self.peer_list.append(peer)
        self.losses[peer] = 0

        _print_("DBS: inserted peer", peer)

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
        sys.stdout.write(Color.green)
        print(serve_socket.getsockname(), '\b: DBS: accepted connection from peer', \
              incomming_peer)
        sys.stdout.write(Color.none)
        self.send_configuration(serve_socket)
        self.send_the_list_of_peers(serve_socket)
        self.insert_peer(incomming_peer)
        serve_socket.close()
        return incomming_peer
                
        # }}}
        
    def receive_message(self):
        # {{{

        try:
            return self.team_socket.recvfrom(struct.calcsize("H"))
        except:
            if __debug__:
                print("DBS: Unexpected error:", sys.exc_info()[0])
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
            if __debug__:
                print("DBS: the unsupportive peer", peer, "does not exist!")
        else:
            if __debug__:
                sys.stdout.write(Color.blue)
                print("DBS: ", peer, "has loss", self.losses[peer], "chunks")
                sys.stdout.write(Color.none)
            if self.losses[peer] > self.MAX_CHUNK_LOSS:
                if peer != self.peer_list[0]:
                    sys.stdout.write(Color.red)
                    print("DBS: ", peer, 'removed')
                    self.remove_peer(peer)
                    sys.stdout.write(Color.none)
        finally:
           pass

        # }}}

    def process_lost_chunk(self, lost_chunk_number, sender):
        # {{{

        destination = self.get_losser(lost_chunk_number)

        if __debug__:
            
            sys.stdout.write(Color.cyan)
            print("DBS: ", sender, "complains about lost chunk", lost_chunk_number, "sent to", destination)
            sys.stdout.write(Color.none)

            if destination == self.peer_list[0]:
                print ("DBS: lost chunk index =", lost_chunk_number)

        self.increment_unsupportivity_of_peer(destination)

        # }}}

    def process_goodbye(self, peer):
        # {{{

        sys.stdout.write(Color.green)
        print('DBS: Received "goodbye" from', peer)
        sys.stdout.write(Color.none)
        sys.stdout.flush()

        #if peer != self.peer_list[0]:
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
            time.sleep(common.COUNTERS_TIMING)

        # }}}

    def compute_next_peer_number(self, peer):
        self.peer_number = (self.peer_number + 1) % len(self.peer_list)

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
            except IndexError:
                if __debug__:
                    _print_("DBS: The monitor peer has died!")


        # }}}

    # }}}

