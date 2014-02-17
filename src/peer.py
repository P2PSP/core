#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# {{{ GNU GENERAL PUBLIC LICENSE

# This is the splitter node of the P2PSP (Peer-to-Peer Simple Protocol)
# <https://launchpad.net/p2psp>.
#
# Copyright (C) 2014 Vicente González Ruiz,
#                    Cristóbal Medina López,
#                    Juan Alvaro Muñoz Naranjo.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# }}}

# This code implements the DBS peer side of the P2PSP.

# {{{ Imports

import sys
import socket
import struct
import time
import argparse
#import threading
from color import Color

# }}}

IP_ADDR = 0
PORT = 1

class Peer_DBS():
    player_port = 9999
    splitter_addr = "150.214.150.68"
    splitter_port = 4552
    port = 0
    debt_threshold = 10 # This value depends on debt_memory
    debt_memory = 1024

    def __init__(self):
        # {{{
        
        print "Peer running in",
        if __debug__:
            print "debug mode"
        else:
            print "release mode"
        print "DBS implemented"

        print "Player port =", self.player_port
        print "Splitter IP address =", self.splitter_addr
        print "Splitter port =", self.splitter_port
        print "(Team) Port =", self.port

        self.peer_list = []
        self.buffer_size = 0
        self.player_alive = True
        self.chunk_number = 0
        self.chunk_size = 0
        self.receive_and_feed_counter = 0
        self.receive_and_feed_previous = ""
        self.received = []
        self.debt = {}
        self.team_socket = ""

        # }}}

    def say_hello(self, peer, team_socket):
        pass

    def say_goodbye(self, peer, team_socket):
        team_socket.sendto('', peer)

    def retrieve_the_list_of_peers(self, splitter_socket, team_socket):
        # {{{

        sys.stdout.write(Color.green)
        print "Requesting the list of peers to", splitter_socket.getpeername()
        number_of_peers = socket.ntohs(struct.unpack("H",splitter_socket.recv(struct.calcsize("H")))[0])
        print "The size of the team is", number_of_peers, "(apart from me)"

        while number_of_peers > 0:
            message = splitter_socket.recv(struct.calcsize("4sH"))
            IP_addr, port = struct.unpack("4sH", message) # Ojo, !H ????
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            peer = (IP_addr, port)
            self.say_hello(peer, team_socket)
            print "[%5d]" % number_of_peers, peer
            self.peer_list.append(peer)
            self.debt[peer] = 0
            number_of_peers -= 1

        print "List of peers received"
        sys.stdout.write(Color.none)

        # }}}

    def run(self):

        # {{{ Setup "player_socket" and wait for the player

        player_socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
        try:
            # In Windows systems this call doesn't work!
            player_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass
        player_socket.bind(('', self.player_port))
        player_socket.listen(0)
        print "Waiting for the player at", player_socket.getsockname()
        player_socket = player_socket.accept()[0]
        #self.player_socket.setblocking(0)
        print "The player is", player_socket.getpeername()

        # }}}

        # {{{ Setup "splitter" and "splitter_socket"

        splitter_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        splitter = (self.splitter_addr, self.splitter_port)
        print "Connecting to the splitter at", splitter
        if self.port != 0:
            try:
                splitter_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            except:
                pass
            sys.stdout.write(Color.purple)
            print "I'm using port the port", self.port
            sys.stdout.write(Color.none)
            splitter_socket.bind(("", self.port))
        try:
            splitter_socket.connect(splitter)
        except:
            sys.exit("Sorry. Can't connect to the splitter at " + str(splitter))
        print "Connected to the splitter at", splitter

        # }}}

        def _(splitter_socket, player_sock):
            header_size = 1024*10
            received = 0
            data = ""
            while received < header_size:
                data = splitter_socket.recv(header_size - received)
                received += len(data)
                try:
                    player_sock.sendall(data)
                except:
                    print "error sending data to the player"
                    print "len(data) =", len(data)
                print "received bytes:", received, "\r",

            print "Received", received, "bytes of header"
        _(splitter_socket, player_socket)

        # {{{ Receive from the splitter the buffer size

        def _():
            message = splitter_socket.recv(struct.calcsize("H"))
            buffer_size = struct.unpack("H", message)[0]
            buffer_size = socket.ntohs(buffer_size)
            return buffer_size
        self.buffer_size = _()
        print "buffer_size =", self.buffer_size

        # }}}

        # {{{ Receive fron the splitter the chunk size

        def _():
            message = splitter_socket.recv(struct.calcsize("H"))
            chunk_size = struct.unpack("H", message)[0]
            chunk_size = socket.ntohs(chunk_size)
            return chunk_size
        self.chunk_size = _()
        print "chunk_size =", self.chunk_size

        # }}}


        # {{{ Create "team_socket" (UDP) as a copy of "splitter_socket" (TCP)

        self.team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # In Windows systems this call doesn't work!
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass
        self.team_socket.bind(('',splitter_socket.getsockname()[PORT]))

        # This is the maximum time the peer will wait for a chunk
        # (from the splitter or from another peer).
        self.team_socket.settimeout(1)

        # }}}

        # {{{ Retrieve the list of peers

        self.retrieve_the_list_of_peers(splitter_socket, self.team_socket)

        # }}}

        splitter_socket.close()
        self.say_hello(splitter, self.team_socket)

        # {{{ Define the buffer of chunks structure

        # Now it is time to define the buffer of chunks, a structure
        # that is used to delay the playback of the chunks in order to
        # accommodate the network jittter. Two components are needed:
        # (1) the "chunks" buffer that stores the received chunks and
        # (2) the "received" buffer that stores if a chunk has been
        # received or not. Notice that each peer can use a different
        # buffer_size: the smaller the buffer size, the lower start-up
        # time, the higher chunk-loss ratio. However, for the sake of
        # simpliticy, all peers will use the same buffer size.

        chunks = [""]*self.buffer_size
        self.received = [False]*self.buffer_size
        numbers = [0]*self.buffer_size
        for i in xrange(0, self.buffer_size):
            numbers[i] = 0

        # }}}

        total_chunks = 0

        def receive_and_feed(team_socket):
            # {{{

            try:
                # {{{ Receive and send

                chunk_format_string = "H" + str(self.chunk_size) + "s"
                message, sender = team_socket.recvfrom(struct.calcsize(chunk_format_string))

                # {{{ debug
                if __debug__:
                    print Color.cyan, "Received a message from", sender, \
                        "of length", len(message), Color.none
                # }}}

                if len(message) == struct.calcsize(chunk_format_string):
                    # {{{ A video chunk has been received

                    number, chunk = struct.unpack(chunk_format_string, message)
                    chunk_number = socket.ntohs(number)

                    chunks[chunk_number % self.buffer_size] = chunk
                    self.received[chunk_number % self.buffer_size] = True
                    numbers[chunk_number % self.buffer_size] = chunk_number

                    if sender == splitter:
                        # {{{ Send the previous chunk in burst sending
                        # mode if the chunk has not been sent to all
                        # the peers of the list of peers.

                        # {{{ debug

                        if __debug__:
                            print team_socket.getsockname(), \
                                Color.red, "<-", Color.none, chunk_number, "-", sender

                        # }}}

                        while( (self.receive_and_feed_counter < len(self.peer_list)) and (self.receive_and_feed_counter > 0) ):
                            peer = self.peer_list[self.receive_and_feed_counter]
                            team_socket.sendto(self.receive_and_feed_previous, peer)

                            # {{{ debug
                            if __debug__:
                                print team_socket.getsockname(), "-",\
                                    socket.ntohs(struct.unpack(chunk_format_string, self.receive_and_feed_previous)[0]),\
                                    Color.green, "->", Color.none, peer
                            # }}}

                            self.debt[peer] += 1
                            if self.debt[peer] > self.debt_threshold:
                                del self.debt[peer]
                                self.peer_list.remove(peer)
                                print Color.red, peer, 'removed by unsupportive', Color.none

                            self.receive_and_feed_counter += 1

                        self.receive_and_feed_counter = 0
                        self.receive_and_feed_previous = message

                       # }}}
                    else:
                        # {{{ The sender is a peer

                        # {{{ debug

                        if __debug__:
                            print team_socket.getsockname(), \
                                Color.green, "<-", Color.none, chunk_number, "-", sender

                        # }}}

                        if sender not in self.peer_list:
                            # The peer is new
                            self.peer_list.append(sender)
                            self.debt[sender] = 0
                            print Color.green, sender, 'added by data chunk', \
                                chunk_number, Color.none
                        else:
                            self.debt[sender] -= 1

                        # }}}

                    # {{{ A new chunk has arrived from a peer and the
                    # previous must be forwarded to next peer of the
                    # list of peers.
                    if ( self.receive_and_feed_counter < len(self.peer_list) and ( self.receive_and_feed_previous != '') ):
                        # {{{ Send the previous chunk in congestion avoiding mode.

                        peer = self.peer_list[self.receive_and_feed_counter]
                        team_socket.sendto(self.receive_and_feed_previous, peer)

                        self.debt[peer] += 1
                        if self.debt[peer] > 10:
                            del self.debt[peer]
                            self.peer_list.remove(peer)
                            print Color.red, peer, 'removed by unsupportive', Color.none

                        # {{{ debug
                        if __debug__:
                            print team_socket.getsockname(), "-", \
                                socket.ntohs(struct.unpack(chunk_format_string, self.receive_and_feed_previous)[0]),\
                                Color.green, "->", Color.none, peer
                        # }}}

                        self.receive_and_feed_counter += 1        

                        # }}}
                    # }}}
                    return chunk_number

                    # }}}
                else:
                    # {{{ A control chunk has been received

                    if sender not in self.peer_list:
                        #print Color.green, sender, 'added by \"hello\" message', Color.none
                        #self.peer_list.append(sender)
                        #self.debt[sender] = 0
                        pass
                    else:
                        sys.stdout.write(Color.red)
                        print team_socket.getsockname(), '\b: received "goodbye" from', sender
                        sys.stdout.write(Color.none)
                        self.peer_list.remove(sender)
                        del self.debt[sender]
                    return -1

                    # }}}

                # }}}
            except socket.timeout:
                return -2

            # }}}

        # This "private and static" variable holds the previous chunk
        # received from the splitter. It is used to send the previous
        # received chunk in the congestion avoiding mode. In that
        # mode, the peer sends a chunk only when it received a chunk
        # from another peer or om the splitter.
        #receive_and_feed.previous = ''

        # Number of times that the previous received chunk has been sent
        # to the team. If this counter is smaller than the number
        # of peers in the team, the previous chunk must be sent in the
        # burst mode because a new chunk from the splitter has arrived
        # and the previous received chunk has not been sent to all the
        # peers of the team. This can happen when one o more chunks
        # that were routed towards this peer have been lost.
        #receive_and_feed.counter = 0

        #  Wall time (execution time plus waiting time).
        start_latency = time.time()

        # {{{ Buffering

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

        print self.team_socket.getsockname(), "\b: buffering ",
        sys.stdout.flush()

        # First chunk to be sent to the player.
        self.chunk_number = receive_and_feed(self.team_socket)

        # The receive_and_feed() procedure returns if a packet has been
        # received or if a time-out exception has been arised. In the first
        # case, the returned value is -1 if the packet contains a
        # hello/goodbyte message or a number >= 0 if a chunk has been
        # received. A -2 is returned if a time-out is has happened.
        while self.chunk_number < 0:
            self.chunk_number = receive_and_feed(self.team_socket)
        self.chunk_to_play = self.chunk_number
        print "First chunk to play", self.chunk_to_play

        # Fill up to the half of the buffer
        for x in xrange(self.buffer_size/2):
            print "\b!",
            sys.stdout.flush()
            while receive_and_feed(self.team_socket) < 0:
                pass

        # }}}

        print 'latency =', time.time() - start_latency, 'seconds'

        def complain(chunk):

            # Complain to the splitter.
            message = struct.pack("!H", chunk)
            self.team_socket.sendto(message, splitter)

            sys.stdout.write(Color.blue)
            print "lost chunk:", numbers[chunk], chunk
            sys.stdout.write(Color.none)            

        def send_next_chunk_to_the_player(player_socket):
            # {{{

            while not self.received[self.chunk_to_play % self.buffer_size]:
                self.chunk_to_play = (self.chunk_to_play + 1) % 65536
                checked_chunk = (self.chunk_to_play + self.buffer_size/2 - 10) % self.buffer_size
                if not self.received[checked_chunk]:
                    complain(checked_chunk)

            try:
                player_socket.sendall(chunks[self.chunk_to_play % self.buffer_size])
            except socket.error:
                print 'Player disconected, ...',
                self.player_alive = False

            # We have fired the chunk.
            self.received[self.chunk_to_play % self.buffer_size] = False

            return self.chunk_to_play

            # }}}

        while self.player_alive:

            #sys.stdout.write("\033[2J\033[;H")
            self.chunk_number = receive_and_feed(self.team_socket)
            #print self.chunk_number, self.chunk_to_play
            #print self.chunk_number - self.chunk_to_play
            while (self.chunk_number - self.chunk_to_play) < self.buffer_size/2:
                #sys.stdout.write(Color.yellow)
                #print "*\b",
                self.chunk_number = receive_and_feed(self.team_socket)
            #sys.stdout.write(Color.none)

            if self.chunk_number >= 0:

                while (self.chunk_number - self.chunk_to_play) > self.buffer_size/2:
                    played_chunk = send_next_chunk_to_the_player(player_socket)

                if (self.chunk_number % self.debt_memory) == 0:
                    for i in self.debt:
                        self.debt[i] /= 2

                for i in xrange(self.buffer_size):
                    if self.received[i]:
                        sys.stdout.write(str(i%10))
                    else:
                        sys.stdout.write('.')
                print
                sys.stdout.write(Color.cyan)
                print "Number of peers in the team:", len(self.peer_list)+1
                print self.team_socket.getsockname(),
                for p in self.peer_list:
                    print p,
                print
                sys.stdout.write(Color.none)

        # The player has gone. Lets do a polite farewell.
        print 'goodbye!'
        goodbye = ''
        self.say_goodbye(splitter, self.team_socket)
        #self.team_socket.sendto(goodbye, splitter)
        print '"goodbye" message sent to the splitter', splitter
        for x in xrange(3):
            receive_and_feed(self.team_socket)
        for peer in self.peer_list:
            self.say_goodbye(splitter, self.team_socket)
            #team_socket.sendto(goodbye, peer)

class Peer_EMS(Peer_DBS):

    def __init__(self):
        Peer_DBS.__init__(self)
        print "EMS implemented"

    def say_hello(self, peer, team_socket):
        team_socket.sendto('H', peer)

    def say_goodbye(self, peer, team_socket):
        team_socket.sendto('G', peer)

def main():

     # {{{ Args parsing
     
     parser = argparse.ArgumentParser(description='This is the peer node of a P2PSP network.')
     parser.add_argument('--debt_threshold', help='Number of times a peer can be unsupportive. (Default = {})'.format(Peer_DBS.debt_threshold))
     parser.add_argument('--player_port', help='Port used to communicate with the player. (Default = "{}")'.format(Peer_DBS.player_port))
     parser.add_argument('--port', help='Port to talk with the peers. (Default = {})'.format(Peer_DBS.port))
     parser.add_argument('--splitter_addr', help='IP address of the splitter. (Default = {})'.format(Peer_DBS.splitter_addr))
     parser.add_argument('--splitter_port', help='Listening port of the splitter. (Default = {})'.format(Peer_DBS.splitter_port))

     args = parser.parse_known_args()[0]
     if args.debt_threshold:
         Peer_DBS.debt_threshold = int(args.debt_threshold)
     if args.player_port:
         Peer_DBS.player_port = int(args.player_port)
     if args.splitter_addr:
         Peer_DBS.splitter_addr = socket.gethostbyname(args.splitter_addr)
     if args.splitter_port:
         Peer_DBS.splitter_port = int(args.splitter_port)
     if args.port:
         Peer_DBS.port = int(args.port)

     # }}}

     peer = Peer_DBS()
#     peer = Peer_EMS()
     peer.run()

if __name__ == "__main__":
     main()

