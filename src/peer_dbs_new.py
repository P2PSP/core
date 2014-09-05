# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# {{{

from __future__ import print_function
import threading
import sys
import socket
import struct
from color import Color
import common
import time
from _print_ import _print_
from peer_ims import Peer_IMS

# }}}

# Some useful definitions.
ADDR = 0
PORT = 1

# DBS: Data Broadcasting Set of rules
class Peer_DBS(Peer_IMS):
    # {{{

    # {{{ Class "constants"

    MAX_CHUNK_DEBT = 32

    # }}}

    def __init__(self, peer):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Peer DBS (no list)")
        sys.stdout.write(Color.none)

        threading.Thread.__init__(self)

        self.splitter_socket = peer.splitter_socket
        self.player_socket = peer.player_socket
        self.buffer_size = peer.buffer_size
        self.splitter = peer.splitter
        self.chunk_size = peer.chunk_size
        self.standard_message_format = peer.message_format
        self.extended_message_format = peer.message_format + "4sH"
        
        _print_("max_chunk_debt =", self.MAX_CHUNK_DEBT)

        # }}}

    def receive_the_chunk_size(self): # Borrar
        # {{{

        Peer_IMS.receive_the_chunk_size(self)
        self.extended_message_format = self.message_format + "4sH"
        if __debug__:
            print ("extended_message_format = ", self.extended_message_format)

        # }}}
        
    def say_goodbye(self, node):
        # {{{

        self.team_socket.sendto('', node)

        # }}}

    def receive_the_number_of_peers(self):
        # {{{

        self.debt = {}      # Chunks debts per peer.
        self.peer_list = [] # The list of peers structure.

        sys.stdout.write(Color.green)
        _print_("Requesting the number of peers to", self.splitter_socket.getpeername())
        self.number_of_peers = socket.ntohs(struct.unpack("H",self.splitter_socket.recv(struct.calcsize("H")))[0])
        _print_("The size of the team is", self.number_of_peers, "(apart from me)")

        sys.stdout.write(Color.none)

        # }}}

    def receive_my_endpoint(self):
        # {{{

        message = self.splitter_socket.recv(struct.calcsize("4sH"))
        IP_addr, port = struct.unpack("4sH", message) # Ojo, !H ????
        IP_addr = socket.inet_ntoa(IP_addr)
        port = socket.ntohs(port)
        self.me = (IP_addr, port)
        _print_("me =", self.me)

        # }}}
        
    def listen_to_the_team(self):
        # {{{ Create "team_socket" (UDP) as a copy of "splitter_socket" (TCP)

        self.team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # In Windows systems this call doesn't work!
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception, e:
            print (e)
            pass
        self.team_socket.bind(('', self.splitter_socket.getsockname()[PORT]))

        # This is the maximum time the peer will wait for a chunk
        # (from the splitter or from another peer).
        self.team_socket.settimeout(1)

        # }}}

    def receive_the_next_message(self):
        # {{{

        #if __debug__:
        #    print ("Waiting for a chunk at {} ...".format(self.team_socket.getsockname()))

        message, sender = self.team_socket.recvfrom(struct.calcsize(self.extended_message_format))
        #print(self.team_socket.getsockname(), struct.calcsize(self.extended_message_format), len(message))
        self.recvfrom_counter += 1

        # {{{ debug

        #if __debug__:
        #    print (Color.cyan, "Received a message from", sender, \
        #        "of length", len(message), Color.none)

        # }}}

        return message, sender

        # }}}

    def process_next_message(self):
        # {{{ 

        try:
            message, sender = self.receive_the_next_message()

            if len(message) == struct.calcsize(self.extended_message_format):
                # {{{ An extended message has been received
                
                # {{{ Decode the message

                chunk_number, chunk, IP_addr, port = struct.unpack(self.extended_message_format, message)
                chunk_number = socket.ntohs(chunk_number)
                incomming_peer = (socket.inet_ntoa(IP_addr), socket.ntohs(port))

                # }}}
                
                if len(self.previous_message) == struct.calcsize(self.standard_message_format):
                    # {{{ Decode the previous message

                    prev_chunk_number, prev_chunk = struct.unpack(self.standard_message_format, \
                                                                  self.previous_message)

                    # }}}
                    # {{{ Attach to the previous splitter's message the new incomming peer

                    self.previous_message = struct.pack(self.extended_message_format, \
                                                        prev_chunk_number, \
                                                        prev_chunk, \
                                                        IP_addr, \
                                                        port)

                    # }}}
                elif len(self.previous_message) == struct.calcsize(self.extended_message_format):
                    # {{{ Decode the previous splitter's message

                    prev_chunk_number, prev_chunk, prev_IP_addr, prev_port = \
                      struct.unpack(self.extended_message_format, self.previous_message)

                    # }}}
                    # {{{ Replace the previous incomming peer by the new one

                    self.previous_message = struct.pack(self.extended_message_format, \
                                                        prev_chunk_number,
                                                        prev_chunk,
                                                        IP_addr, \
                                                        port)

                    # }}}
                
                if (incomming_peer not in self.peer_list) and (incomming_peer != self.me):
                    # {{{ Insert the incomming peer in the list of peers

                    self.peer_list.append(incomming_peer) # Ojo, colocar como siguiente, no al final
                    self.debt[incomming_peer] = 0
                    _print_(Color.green, incomming_peer, '--(long)--> added by chunk', chunk_number, Color.none)

                    # }}}
                    
                # }}}
            elif len(message) == struct.calcsize(self.standard_message_format):
                # {{{ A standard message has been received

                # {{{ Decode the message

                chunk_number, chunk = struct.unpack(self.standard_message_format, message)
                chunk_number = socket.ntohs(chunk_number)

                # }}}

                # }}}
            else:
                _print_(Color.red + "Unexpected message length =", len(message), Color.none)

            self.chunks[chunk_number % self.buffer_size] = chunk
            self.received[chunk_number % self.buffer_size] = True

            if sender == self.splitter:
                # {{{ Retransmit the previous splitter's message in burst
                # transmission mode

                # {{{ debug

                if __debug__:
                    _print_(self.team_socket.getsockname(), \
                        Color.red, "<-", Color.none, chunk_number, "-", sender)

                # }}}

                while (self.eat_and_feed_counter < len(self.peer_list)) and (self.eat_and_feed_counter > 0):
                    # {{{
                    peer = self.peer_list[self.eat_and_feed_counter]
                    self.team_socket.sendto(self.previous_message, peer)
                    self.sendto_counter += 1

                    # {{{ debug

                    if __debug__:
                        print (self.team_socket.getsockname(), "-",\
                            socket.ntohs(struct.unpack(self.standard_message_format, \
                                                           self.previous_message)[0]),\
                            Color.green, "->", Color.none, peer)

                    # }}}

                    self.debt[peer] += 1
                    if self.debt[peer] > self.MAX_CHUNK_DEBT:
                        del self.debt[peer]
                        self.peer_list.remove(peer)
                        print (Color.red, peer, 'removed by unsupportive', Color.none)

                    self.eat_and_feed_counter += 1
                    # }}}

                self.eat_and_feed_counter = 0
                self.previous_message = message

                if len(self.peer_list) < self.number_of_peers:
                    _print_("len(peer_list) =", len(self.peer_list), "number_of_peers =", self.number_of_peers)

                # }}}
            else:
                # {{{ If the sender peer is new, insert it in the list of peers

                # {{{ debug

                if __debug__:
                    print (self.team_socket.getsockname(), \
                        Color.green, "<-", Color.none, chunk_number, "-", sender)

                # }}}

                if sender not in self.peer_list:
                    self.peer_list.append(sender)
                    self.debt[sender] = 0
                    print (Color.green, sender, 'added by chunk', \
                        chunk_number, Color.none)
                else:
                    self.debt[sender] -= 1

                # }}}
                
            # {{{ Retransmit the previous splitter's message using the congestion avoid transmission mode 
            if ( self.eat_and_feed_counter < len(self.peer_list) and ( self.previous_message != '') ):
                # {{{ Send the previous chunk in congestion avoiding mode.

                peer = self.peer_list[self.eat_and_feed_counter]
                self.team_socket.sendto(self.previous_message, peer)
                self.sendto_counter += 1

                self.debt[peer] += 1
                if self.debt[peer] > self.MAX_CHUNK_DEBT:
                    del self.debt[peer]
                    self.peer_list.remove(peer)
                    print (Color.red, peer, 'removed by unsupportive', Color.none)

                # {{{ debug

                if __debug__:
                    if len(self.previous_message) == struct.calcsize(self.standard_message_format):
                        print (self.team_socket.getsockname(), "-", \
                            socket.ntohs(struct.unpack(self.standard_message_format, self.previous_message)[0]),\
                            Color.green, "->", Color.none, peer)
                    else:
                        print (self.team_socket.getsockname(), "-", \
                            socket.ntohs(struct.unpack(self.extended_message_format, self.previous_message)[0]),\
                            Color.green, "->", Color.none, peer)
              

                # }}}

                self.eat_and_feed_counter += 1

                # }}}

            # }}}

            return chunk_number
        
        except socket.timeout:
            return -2

        # }}}
        
    def process_next_message2(self):
        try:
            message, sender = self.receive_the_next_message()

            chunk = ""
            chunk_number = 0

            if len(message) == struct.calcsize(self.extended_message_format):
                # {{{ Message with a new peer. Extract: chunk_number, chunk and the incomming_peer
                
                #print(self.extended_message_format)
                chunk_number, chunk, IP_addr, port = struct.unpack(self.extended_message_format, message)
                chunk_number = socket.ntohs(chunk_number)
                #IP_addr, port = struct.unpack("4sH", incomming_peer)
                incomming_peer = (socket.inet_ntoa(IP_addr), socket.ntohs(port))

                # }}}

                #print("---------------->", incomming_peer, self.me)
                if (incomming_peer not in self.peer_list) and (incomming_peer != self.me):
                #if True:
                #if incomming_peer[1] != self.me[1]:
                    # {{{ Insert the incomming peer in the list of peers

                    self.peer_list.append(incomming_peer) # Ojo, colocar como siguiente, no al final
                    self.debt[incomming_peer] = 0
                    _print_(Color.green, incomming_peer, '--(long)--> added by chunk', chunk_number, Color.none)

                    # }}}
                    
            else:
                # {{{ Normal message. Extract chunk_number and chunk
                try:
                    chunk_number, chunk = struct.unpack(self.standard_message_format, message)
                except:
                    _print_(Color.red + "Unexpected message length =", len(message), Color.none)
                    
                chunk_number = socket.ntohs(chunk_number)

                # }}}
                
            #print("--> chunk_nunber =", chunk_number, "sender =", sender)
            self.chunks[chunk_number % self.buffer_size] = chunk
            self.received[chunk_number % self.buffer_size] = True

            if sender == self.splitter:
                # {{{ Retransmit the previous splitter's message in burst transmission mode

                #_print_(self.team_socket.getsockname(), Color.red, "<-", Color.none, chunk_number, "-", sender)
                #print("--------- eat_and_feed_counter =", self.eat_and_feed_counter)
                #while( (self.eat_and_feed_counter < len(self.peer_list)) and (self.eat_and_feed_counter > 0) ):
                while self.eat_and_feed_counter < len(self.peer_list):
                    peer = self.peer_list[self.eat_and_feed_counter]
                    #_print_("Sending (burst) to", peer, "the chunk", chunk_number-1) 
                    self.team_socket.sendto(self.previous_message, peer)

                    ## _print_(self.team_socket.getsockname(), "-", \
                    ##         socket.ntohs(struct.unpack(self.standard_message_format, \
                    ##                                    self.previous_message)[0]), \
                    ##                                    Color.green, "->", Color.none, peer)
                    
                    #self.team_socket.sendto(message, peer)
                    self.sendto_counter += 1

                    self.debt[peer] += 1
                    if self.debt[peer] > self.MAX_CHUNK_DEBT:
                        del self.debt[peer]
                        self.peer_list.remove(peer)
                        print (Color.red, peer, 'removed by unsupportive', Color.none)

                    self.eat_and_feed_counter += 1

                self.eat_and_feed_counter = 0
                self.previous_message = message

                # }}}
            else:
                # {{{ Retransmit the previous splitter's message in congestion avoid transmission mode

                #print("------------ eat_and_feed_counter =", self.eat_and_feed_counter, "len(self.previous_message) =", len(self.previous_message))
                #if ( self.eat_and_feed_counter < len(self.peer_list) and ( self.previous_message != '') ):
                if self.eat_and_feed_counter < len(self.peer_list):

                    peer = self.peer_list[self.eat_and_feed_counter]
                    #_print_("Sending (congestion avoid) to", peer, "the chunk", chunk_number-1) 
                    self.team_socket.sendto(self.previous_message, peer)
                    self.sendto_counter += 1

                    self.debt[peer] += 1
                    if self.debt[peer] > self.MAX_CHUNK_DEBT:
                        del self.debt[peer]
                        self.peer_list.remove(peer)
                        print (Color.red, peer, 'removed by unsupportive', Color.none)

                    self.eat_and_feed_counter += 1

                if sender not in self.peer_list:
                    # The peer is new
                    self.peer_list.append(sender)
                    self.debt[sender] = 0
                    _print_(Color.green, sender, '--(short)--> added by chunk', \
                        chunk_number, Color.none)
                else:
                    self.debt[sender] -= 1
                
                # }}}
                
            return chunk_number

        except socket.timeout:
            return -2

    def keep_the_buffer_full(self):
        # {{{

        Peer_IMS.keep_the_buffer_full(self)
        if (self.played_chunk % self.debt_memory) == 0:
            for i in self.debt:
                self.debt[i] /= 2

        ## if __debug__:
        ##     sys.stdout.write(Color.cyan)
        ##     print ("Number of peers in the team:", len(self.peer_list)+1)
        ##     print (self.team_socket.getsockname(),)
        ##     for p in self.peer_list:
        ##         print (p,)
        ##     print ()
        ##     sys.stdout.write(Color.none)

        # }}}

    def polite_farewell(self):
        # {{{

        print('Goodbye!')
        for x in xrange(3):
            self.say_goodbye(self.splitter)
        while self.eat_and_feed_counter < len(self.peer_list):
            self.process_next_message()
        #for peer in self.peer_list:
            #self.say_goodbye(peer)

        # }}}

    def buffer_data(self):
        # {{{

        # Number of times that the previous received chunk has been sent
        # to the team. If this counter is smaller than the number
        # of peers in the team, the previous chunk must be sent in the
        # burst mode because a new chunk from the splitter has arrived
        # and the previous received chunk has not been sent to all the
        # peers of the team. This can happen when one o more chunks
        # that were routed towards this peer have been lost.
        self.eat_and_feed_counter = 0

        # This "private and static" variable holds the previous chunk
        # received from the splitter. It is used to send the previous
        # received chunk in the congestion avoiding mode. In that
        # mode, the peer sends a chunk only when it received a chunk
        # from another peer or om the splitter.
        self.previous_message = ""

        self.sendto_counter = 0

        self.debt_memory = 1 << self.MAX_CHUNK_DEBT

        Peer_IMS.buffer_data(self)

        # }}}
        
    def run(self):
        # {{{

        Peer_IMS.peers_life(self)
        self.polite_farewell()

        # }}}

    def am_i_a_monitor(self):
        # Esto hay que cambiarlo porque se podria predecir quien es el monitor y eso no interesa.
        if self.number_of_peers == 0:
            # Only the first peer of the team is the monitor peer
            return True
        else:
            return False
        #message = self.splitter_socket.recv(struct.calcsize("c"))
        #if struct.unpack("c", message)[0] == '1':
        #    return True
        #else:
        #    return False

    # }}}
