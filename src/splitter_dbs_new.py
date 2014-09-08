# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# Cuando un peer X se conecta al splitter, éste le envía sólo la
# configuración básica. A continuación inserta al peer en la lista
# junto a continuación del último peer recorrido con la idea que se
# tarde el máximo tiempo posible en enviar un chunk exclusivo al peer
# entrante. La idea es que el peer entrante reciba primero un chunk
# desde cada uno de los peers del team antes de recibir el primer
# chunk desde el splitter, para que de esta forma su lista de peers
# esté llena en ese momento. A continuación el splitter añade al
# siguiente chunk a transmitir el end-point del peer X: [X]
# (dependiendo de un parámetro de configuración, este proceso podría
# realizarse para algunos chunks más lo que ayudaría en entornos
# ruidosos, donde estos chunks pueden perderse facilmente). Este chunk
# con [X] será recibido por un peer Y que comprobará que se trata de
# un chunk especial, en el que figura [X], el end-point de un nuevo
# peer en el team. Y insertará [X] en su lista de peers y
# retransmitirá el chunk al resto del team. El resto del team hará lo
# mismo. Los peer evitarán añadir a sus lista de peers end-points ya
# existentes (como ocurre actualmente).

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
    MAX_CHUNK_LOSS = 16
    MCAST_ADDR = "0.0.0.0"

    # }}}

    def __init__(self):
        # {{{

        Splitter_IMS.__init__(self)

        self.INCOMMING_PEER_COUNTER = 13

        self.print_modulename()
        #self.number_of_monitors = 0
        self.peer_number = 0

        # {{{ The list of peers in the team.
        # }}}
        self.peer_list = []
        
        # {{{ Destination peers of the chunk, indexed by a chunk
        # number. Used to find the peer to which a chunk has been
        # sent.
        # }}}
        self.destination_of_chunk = [('0.0.0.0',0)] * self.BUFFER_SIZE
        #for i in xrange(self.BUFFER_SIZE):
        #    self.destination_of_chunk.append(('0.0.0.0',0))

        self.losses = {}

        # }}}

    def print_modulename(self):
        # {{{

        sys.stdout.write(Color.yellow)
        print("Splitter DBS (no list)")
        sys.stdout.write(Color.none)

        # }}}

    def say_goodbye(self, node, sock):
        # {{{

        sock.sendto('', node)

        # }}}

    # Borrar ???
    def send_the_list_size(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("Sending a list of peers of size", len(self.peer_list))
        message = struct.pack("H", socket.htons(len(self.peer_list)))
        peer_serve_socket.sendall(message)

        # }}}

    def send_the_peer_endpoint(self, peer_serve_socket):
        # {{{

        peer_endpoint = peer_serve_socket.getpeername()
        message = struct.pack("4sH", socket.inet_aton(peer_endpoint[ADDR]), socket.htons(peer_endpoint[PORT]))
        peer_serve_socket.sendall(message)

        # }}}

    # Pensar en reutilizar Splitter_IMS.handle_peer_arrival()
    # concatenando las llamadas a las funciones.

    def send_configuration(self, sock):
        # {{{

        Splitter_IMS.send_configuration(self, sock)
        self.send_the_list_size(sock)
        self.send_the_peer_endpoint(sock)

        # }}}
        
    def insert_peer(self, peer):
        # {{{
        if peer not in self.peer_list: # Probar a quitar -----------------------------------------------------
            self.peer_list.insert(self.peer_number, peer)
            #self.peer_list.append(peer)
        self.losses[peer] = 0

        # }}}

    def handle_a_peer_arrival(self, connection):
        # {{{

        # {{{ In the DBS, the splitter sends to the incomming peer the
        # list of peers. Notice that the transmission of the list of
        # peers (something that could need some time if the team is
        # big or if the peer is slow) is done in a separate thread. This
        # helps to avoid DoS (Denial of Service) attacks.
        # }}}

        tmp_list_runs = self.list_runs
        Splitter_IMS.handle_a_peer_arrival(self, connection)
        peer = connection[1]
        self.incomming_peer = peer
        self.incomming_peer_counter = self.INCOMMING_PEER_COUNTER
        ## if len(self.peer_list) > 0:
        ##     while (self.list_runs - tmp_list_runs) < 2:
        ##         _print_("longitud de la lista =", len(self.peer_list))
        ##         _print_("self.list_runs =", self.list_runs)
        ##         _print_("tmp_list_runs =", tmp_list_runs)
        ##         _print_("self.list_runs - tmp_list_runs =", self.list_runs - tmp_list_runs)
        ##         time.sleep(1)
        
        #self.insert_peer(peer)

        # }}}

    def receive_message(self):
        # {{{

        return self.team_socket.recvfrom(struct.calcsize("H"))

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
            print("the unsupportive peer", peer, "does not exist!")
        else:
            if __debug__:
                sys.stdout.write(Color.blue)
                print(peer, "has loss", self.losses[peer], "chunks")
                sys.stdout.write(Color.none)
            if self.losses[peer] > self.MAX_CHUNK_LOSS:
                sys.stdout.write(Color.red)
                print(peer, 'removed')
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
            print(sender, "complains about lost chunk", lost_chunk_number, "sent to", destination)
            sys.stdout.write(Color.none)

            if destination == self.peer_list[0]:
                print ("lost chunk index =", lost_chunk_number)

        _print_("complain about: ", destination)
        if destination != self.peer_list[0]:
            self.increment_unsupportivity_of_peer(destination)

        # }}}

    def process_goodbye(self, peer):
        # {{{

        sys.stdout.write(Color.green)
        print('Received "goodbye" from', peer)
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

        try:
            # This does not work in Windows systems !!
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass
        try:
            self.team_socket.bind(('', self.PORT))
        except:
            raise

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
        # {{{

        self.peer_number = (self.peer_number + 1) % len(self.peer_list)
        if self.peer_number == 0:
            self.list_runs += 1

        # }}}

    def run(self):
        # {{{

        self.receive_the_header()

        self.list_runs = 0
        
        # {{{ A DBS splitter runs 4 threads. The main one and the
        # "handle_arrivals" thread are equivalent to the daemons used
        # by the IMS splitter. "moderate_the_team" and
        # "reset_counters_thread" are new.
        # }}}

        print(self.peer_connection_socket.getsockname(), "\b: waiting for the monitor peer ...")
        def _():
            connection  = self.peer_connection_socket.accept()
            self.handle_a_peer_arrival(connection)
            self.incomming_peer_counter = 0 # The monitor peer is not announced
            self.insert_peer(self.incomming_peer)
        _()

        threading.Thread(target=self.handle_arrivals).start()
        threading.Thread(target=self.moderate_the_team).start()
        threading.Thread(target=self.reset_counters_thread).start()
        #time.sleep(1)

        #self.incomming_peer_counter = self.INCOMMING_PEER_COUNTER

        #header_load_counter = 0
        while self.alive:

            #chunk = self.receive_chunk(header_load_counter)
            chunk = self.receive_chunk()
            try:
                peer = self.peer_list[self.peer_number]
                #self.compute_next_peer_number(peer)
                if self.incomming_peer_counter > 0:

                    message_format = self.chunk_number_format \
                        + str(self.CHUNK_SIZE) + "s" \
                        + "4sH"

                    message = struct.pack(message_format, \
                        socket.htons(self.chunk_number), \
                        chunk,
                        socket.inet_aton(self.incomming_peer[ADDR]), \
                        socket.htons(self.incomming_peer[PORT]))

                    #self.send_chunk(message, self.incomming_peer)

                    self.incomming_peer_counter -= 1

                    if self.incomming_peer_counter == 0:
                        self.insert_peer(self.incomming_peer)
                        self.compute_next_peer_number(peer)
                
                else:

                    message_format = self.chunk_number_format \
                        + str(self.CHUNK_SIZE) + "s"

                    message = struct.pack(message_format, \
                        socket.htons(self.chunk_number), \
                        chunk)
                        
                #print(len(message), peer, self.incomming_peer_counter)
                self.compute_next_peer_number(peer)
                self.send_chunk(message, peer)

                #print(self.chunk_number)

                self.destination_of_chunk[self.chunk_number % self.BUFFER_SIZE] = peer
                self.chunk_number = (self.chunk_number + 1) % common.MAX_CHUNK_NUMBER
            except IndexError:
                _print_("The monitor peer has died!")


        # }}}

    # }}}

