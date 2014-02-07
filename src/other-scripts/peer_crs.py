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
import threading
from color import Color

# }}}

# Some useful definitions.
IP_ADDR = 0
PORT = 1

class Peer_DBS(threading.Thread):
    player_port = 9999
    splitter_host = "150.214.150.68"
    splitter_port = 4552
    team_port = 0
    losses_threshold = 8

    def __init__(self):
        # {{{

        threading.Thread.__init__(self)
        
        print "Peer running in",
        if __debug__:
            print "debug mode"
        else:
            print "release mode"

        # This is the list of peers of the team. Each peer uses
        # this structure to resend the chunks received from the
        # splitter to these nodes.
        #peer_list = []
        self.peer_list = []
        # This store the insolidarity/losses of the peers of
        # the team. When the insolidarity exceed a threshold, the
        # peer is deleted from the list of peers.
        self.losses = {}
        #self.player_socket = ""
        #self.source_host = ""
        #self.source_port = 0
        #self.channel = ""
        #self.buffer_size = 0
        #self.total_chunks = 0L
        #self.splitter = ""
        #self.player_socket = ""
        #self.team_socket = ""
        #self.splitter_socket = ""
        self.player_alive = True
        self.chunk_number = 0
        self.chunk_size = 0
        self.receive_and_feed_counter = 0
        self.receive_and_feed_last = ""
        # }}}

    def retrieve_the_list_of_peers(self, splitter_socket, team_socket):
        # {{{

        # The list of peers should be retrieved from the splitter in a
        # different thread because in this way, if the retrieving
        # takes a long time, the peer can receive the chunks that
        # other peers are sending to it.

        sys.stdout.write(Color.green)
        print splitter_socket.getsockname(), "\b: requesting the list of peers to", splitter_socket.getpeername()
        number_of_peers = socket.ntohs(struct.unpack("H",splitter_socket.recv(struct.calcsize("H")))[0])
        print splitter_socket.getpeername(), "\b: the size of the list of peers is", number_of_peers

        while number_of_peers > 0:
            message = splitter_socket.recv(struct.calcsize("4sH"))
            IP_addr, port = struct.unpack("4sH", message)
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            peer = (IP_addr, port)
            print "[%5d]" % number_of_peers, peer
            self.peer_list.append(peer)
            self.losses[peer] = 0
            #print Color.green, cluster_socket.getsockname(), \
            #    "-", '"hello"', "->", peer, Color.none
            # Say hello to the peer
            team_socket.sendto('', peer) # Send a empty chunk (this should be fast).
            number_of_peers -= 1

        print 'done'
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
        print player_socket.getsockname(), "\b: waiting for the player ..."
        player_socket = player_socket.accept()[0]
        #self.player_socket.setblocking(0)
        print player_socket.getsockname(), "\b: the player is", player_socket.getpeername()

        # }}}
        # {{{ Setup "splitter" and "splitter_socket"

        splitter_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        splitter = (self.splitter_host, self.splitter_port)
        print splitter_socket.getsockname(), "\b: connecting to the splitter at", splitter
        if self.team_port != 0:
            try:
                splitter_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            except:
                pass
            sys.stdout.write(Color.purple)
            print splitter_socket.getsockname(), "\b: I'm using port the port", self.team_port
            sys.stdout.write(Color.none)
            splitter_socket.bind(("", self.team_port))
        try:
            splitter_socket.connect(splitter)
        except:
            sys.exit("Sorry. Can't connect to the splitter at " + str(splitter))
        print splitter_socket.getsockname(), "\b: connected to the splitter at", splitter

        # }}}
        # {{{ Setup "team_socket"

        team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # In Windows systems this call doesn't work!
            team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass
        team_socket.bind(('',splitter_socket.getsockname()[PORT]))

        # This is the maximum time the peer will wait for a chunk
        # (from the splitter or from another peer).
        team_socket.settimeout(1)

        # }}}
        # {{{ Receive from the splitter the IP address of the source node

        def _():
            message = splitter_socket.recv(struct.calcsize("4s"))
            source_host = struct.unpack("4s", message)[0]
            source_host = socket.inet_ntoa(source_host)
            return source_host
        source_host = _()
        print splitter_socket.getpeername(), "\b: source_host =", source_host

        # }}}
        # {{{ Receive from the splitter the port of the source node

        def _():
            message = splitter_socket.recv(struct.calcsize("H"))
            source_port = struct.unpack("H", message)[0]
            source_port = socket.ntohs(source_port)
            return source_port
        source_port = _()
        print splitter_socket.getpeername(), "\b: source_port =", source_port

        # }}}
        # {{{ Receive from the splitter the channel name

        def _():
            message = splitter_socket.recv(struct.calcsize("H"))
            channel_size = struct.unpack("H", message)[0]
            channel_size = socket.ntohs(channel_size)
            channel = splitter_socket.recv(channel_size)
            return channel
        channel = _()
        print splitter_socket.getpeername(), "\b: channel =", channel

        # }}}
        # {{{ Receive from the splitter the buffer size

        def _():
            message = splitter_socket.recv(struct.calcsize("H"))
            buffer_size = struct.unpack("H", message)[0]
            buffer_size = socket.ntohs(buffer_size)
            return buffer_size
        buffer_size = _()
        print splitter_socket.getpeername(), "\b: buffer_size =", buffer_size

        # }}}
        # {{{ Receive fron the splitter the chunk size

        def _():
            message = splitter_socket.recv(struct.calcsize("H"))
            chunk_size = struct.unpack("H", message)[0]
            chunk_size = socket.ntohs(chunk_size)
            return chunk_size
        self.chunk_size = _()
        print splitter_socket.getpeername(), "\b: chunk_size =", self.chunk_size

        # }}}
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
        #chunks = [None]*buffer_size
        chunks = [""]*buffer_size
        received = [True]*buffer_size
        numbers = [0]*buffer_size
        for i in xrange(0, buffer_size):
            numbers[i] = i

        # }}}

        # {{{ Retrieve the list of peers and sends the [Hello] messages

        threading.Thread(target=self.retrieve_the_list_of_peers, args=(splitter_socket, team_socket,) ).start()

        # }}}

        total_chunks = 0

        # {{{ Relay the header to the player

        # The video header is requested directly to the source node,
        # mainly, because in a concatenation of videos served by the
        # source each video has a different header (another reason is
        # that part of the load is translated from the splitter to the
        # source, which can also perform managing operations such as
        # collecting statistics about the peers). This implies that,
        # if the header of the currently streamed video is served by
        # the splitter, it must be aware of the end of a video and the
        # start of the next, and record the header to serve it to the
        # peers. Notice that, only the header of the first recived
        # video is transmitted over the TCP. The headers of the rest
        # of videos of the received sequence is transmitted over the
        # UDP. It is expectable that, if one of these headers are
        # corrupted by transmission errors, the users will manually
        # restart the conection with the streaming service, using
        # again the TCP.

        def relay_the_header_to_the_player(source, player_sock):
            source_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #source = (source_host, source_port)
            print source_sock.getsockname(), "\b: connecting to the source at", source, "..."
            sys.stdout.flush()
            source_sock.connect(source)
            print source_sock.getsockname(), "\b: connected to", source

            GET_message = 'GET ' + channel + ' HTTP/1.1\r\n'
            GET_message += '\r\n'
            source_sock.sendall(GET_message)

            print source_sock.getsockname(), "\b: requesting the stream header via http://" + str(source_sock.getpeername()[0]) + ':' + str(source_sock.getpeername()[1]) + str(channel)
            header_size = 1024*100

            received = 0
            data = ""

            while received < header_size:
                data = source_sock.recv(header_size - received)
                received += len(data)
                try:
                    player_sock.sendall(data)
                except:
                    print "error sending data to the player"
                    print "len(data) =", len(data)
                print "received bytes:", received, "\r",

            print source_sock.getsockname(), '\b: sent', received, 'bytes'
            source_sock.close()

        relay_the_header_to_the_player((source_host, source_port), player_socket)

        # }}}

        def receive_and_feed():
            # {{{

            try:
                chunk_format_string = "H" + str(self.chunk_size) + "s"
                # {{{ Receive and send

                message, sender = team_socket.recvfrom(struct.calcsize(chunk_format_string))
                if __debug__:
                    print Color.cyan, "Received a message from", sender, \
                        "of length", len(message), Color.none

                if len(message) == struct.calcsize(chunk_format_string):
                    # {{{ A video chunk has been received

                    number, chunk = struct.unpack(chunk_format_string, message)
                    chunk_number = socket.ntohs(number)

#                    total_chunks += 1

                    # Insert the received chunk into the buffer.
                    #print "------------", chunk_number, buffer_size, len(message), len(chunk)
                    chunks[chunk_number % buffer_size] = chunk
                    received[chunk_number % buffer_size] = True
                    numbers[chunk_number % buffer_size] = chunk_number

                    if sender == splitter:
                        # {{{ Send the last chunk in burst sending mode

                        if __debug__:
                            print cluster_socket.getsockname(), \
                                Color.red, "<-", Color.none, chunk_number, "-", sender

                        # A new chunk has arrived from the splitter
                        # and we must check if the last chunk was sent
                        # fo the rest of peers of the cluster.
                        while( (self.receive_and_feed_counter < len(self.peer_list)) and (self.receive_and_feed_counter > 0) ):
                            peer = self.peer_list[self.receive_and_feed_counter]
                            cluster_socket.sendto(self.receive_and_feed_last, peer)
                            if __debug__:
                                print self.team_socket.getsockname(), "-", chunk_number, \
                                    Color.green, "->", Color.none, peer

                            # Each time we send a chunk to a peer, the
                            # losses of that peer is incremented. Each
                            # time we receive a chunk from a peer, the
                            # losses of that peer is decremented.
                                self.losses[peer] += 1

                            # If the losses of a peer exceed a
                            # threshold, the peer is removed from the list of
                            # peers.
                            if self.losses[peer] > self.losses_threshold:
                                sys.stdout.write(Color.red)
                                print 'removing the unsupportive peer', peer
                                sys.stdout.write(Color.none)
                                del self.losses[peer]
                                self.peer_list.remove(peer)
                            self.receive_and_feed_counter += 1
                        self.receive_and_feed_counter = 0
                        self.receive_and_feed_last = message

                       # }}}
                    else:
                        # {{{ The sender is a peer, check if the peer is new.

                        if __debug__:
                            print self.team_socket.getsockname(), \
                                Color.green, "<-", Color.none, chunk_number, "-", sender

                        if sender not in self.peer_list:
                            # The peer is new
                            self.peer_list.append(sender)
                            self.losses[sender] = 0                
                            print Color.green, sender, 'added by data chunk', \
                                chunk_number, Color.none
                        else:
                            self.losses[sender] -= 1;
                            if self.losses[sender] < 0:
                                self.losses[sender] = 0

                        # }}}

                    # A new chunk has arrived and it must be forwarded to the
                    # rest of peers of the cluster.
                    if ( self.receive_and_feed_counter < len(self.peer_list) and ( self.receive_and_feed_last != '') ):
                        # {{{ Send the last chunk in congestion avoiding mode.

                        peer = self.peer_list[self.receive_and_feed_counter]
                        team_socket.sendto(self.receive_and_feed_last, peer)
                        if __debug__:
                            print team_socket.getsockname(), "-", chunk_number,\
                                Color.green, "->", Color.none, peer

                        self.losses[peer] += 1        
                        if self.losses[peer] > self.losses_threshold:
                            sys.stdout.write(Color.red)
                            print peer, 'Removed by unsupportive', "(losses[", "\b", peer, "\b] = ", self.losses[peer], ">", self.losses_threshold
                            sys.stdout.write(Color.none)  
                            del self.losses[peer]
                            self.peer_list.remove(peer)
                        self.receive_and_feed_counter += 1        

                        # }}}

                    return chunk_number

                    # }}}
                else:
                    # {{{ A control chunk has been received

                    if sender not in self.peer_list:
                        print Color.green, sender, 'added by \"hello\" message', Color.none
                        self.peer_list.append(sender)
                        self.losses[sender] = 0
                    else:
                        sys.stdout.write(Color.red)
                        print team_socket.getsockname(), '\b: received "goodbye" from', sender
                        sys.stdout.write(Color.none)
                        self.peer_list.remove(sender)
                    return -1

                    # }}}

                # }}}
            except socket.timeout:
                return -2

            # }}}

        # This "private and static" variable holds the last chunk
        # received from the splitter. It is used to send the last
        # received chunk in the congestion avoiding mode. In that
        # mode, the peer sends a chunk only when it received a chunk
        # from another peer or om the splitter.
        #receive_and_feed.last = ''

        # Number of times that the last received chunk has been sent
        # to the cluster. If this counter is smaller than the number
        # of peers in the cluster, the last chunk must be sent in the
        # burst mode because a new chunk from the splitter has arrived
        # and the last received chunk has not been sent to all the
        # peers of the cluster. This can happen when one o more chunks
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

        print team_socket.getsockname(), "\b: buffering ",
        sys.stdout.flush()

        # Retrieve the first chunk to play.
        self.chunk_number = receive_and_feed()

        # The receive_and_feed() procedure returns if a packet has been
        # received or if a time-out exception has been arised. In the first
        # case, the returned value is -1 if the packet contains a
        # hello/goodbyte message or a number >= 0 if a chunk has been
        # received. A -2 is returned if a time-out is has happened.
        while self.chunk_number < 0:
            self.chunk_number = receive_and_feed()

        # In this moment, the variable chunk_number stores the first chunk to
        # be sent to the player. Notice that the range of the chunk index uses
        # to be much larger than the buffer size. Therefore, a simple hash
        # operation (in the case, the modulo operation) has been used. Because
        # we expect that video chunks come in order and the chunks are sent to
        # the player also in order, this hashing should work fine.
        chunk_to_play = self.chunk_number % buffer_size

        # Fill up to the half of the buffer.
        for x in xrange(buffer_size/2):
            print "\b.",
            sys.stdout.flush()
            while receive_and_feed()<=0:
                pass

        # }}}

        print 'latency =', time.time() - start_latency, 'seconds'

        def send_a_chunk_to_the_player(player_socket):
            # {{{

            if not received[chunk_to_play]:

                # Lets complain to the splitter.
                message = struct.pack("!H", chunk_to_play)
                team_socket.sendto(message, splitter)

                sys.stdout.write(Color.blue)
                print "lost chunk:", numbers[chunk_to_play], chunk_to_play
                sys.stdout.write(Color.none)

            # Ojo, probar a no enviar nada!!!
            #print player_socket.getsockname(), "->", numbers[chunk_to_play], player_socket.getpeername()
            try:
                player_socket.sendall(chunks[chunk_to_play])
            except socket.error:
                print 'Player disconected, ...',
                self.player_alive = False
                return
            '''
            finally:
                #print chunk_to_play, len(chunks[chunk_to_play])
                print "finally"
                return
            '''
            # We have fired the chunk.
            received[chunk_to_play] = False

            # }}}

        while self.player_alive:
            self.chunk_number = receive_and_feed()
            #print "Received", self.chunk_number
            if self.chunk_number >= 0:
                if (self.chunk_number % 256) == 0:
                    for i in self.losses:
                        self.losses[i] /= 2
                send_a_chunk_to_the_player(player_socket)
                chunk_to_play = (chunk_to_play + 1) % buffer_size

        # The player has gone. Lets do a polite farewell.
        print 'goodbye!'
        goodbye = ''
        team_socket.sendto(goodbye, splitter)
        print '"goodbye" message sent to the splitter', splitter
        for x in xrange(3):
            receive_and_feed()
        for peer in self.peer_list:
            team_socket.sendto(goodbye, peer)

def main():

     # {{{ Args parsing
     
     parser = argparse.ArgumentParser(description='This is the peer node of a P2PSP network.')
     parser.add_argument('--player_port', help='Port used to communicate with the player. (Default = "{}")'.format(Peer_DBS.player_port))
     parser.add_argument('--splitter_host', help='Host of the splitter. (Default = {})'.format(Peer_DBS.splitter_host))
     parser.add_argument('--splitter_port', help='Listening port of the splitter. (Default = {})'.format(Peer_DBS.splitter_port))
     parser.add_argument('--team_port', help='Port to talk with the peers. (Default = {})'.format(Peer_DBS.team_port))
     parser.add_argument('--losses_threshold', help='Number of times a peer can be unsupportive. (Default = {})'.format(Peer_DBS.losses_threshold))

     peer = Peer_DBS()

     args = parser.parse_known_args()[0]
     if args.player_port:
         peer.player_port = int(args.player_port)
     if args.splitter_host:
         peer.splitter_host = socket.gethostbyname(args.splitter_host)
     if args.splitter_port:
         peer.splitter_port = int(args.splitter_port)
     if args.team_port:
         peer.team_port = int(args.team_port)
     if args.losses_threshold:
         peer.losses_threshold = int(args.losses_threshold)

     # }}}

     peer.start()
     last_chunk_number = 0
     while peer.player_alive:
           print "[%3d] " % (len(peer.peer_list)+1),
           kbps = (peer.chunk_number - last_chunk_number) * \
               peer.chunk_size * 8/1000
           last_chunk_number = peer.chunk_number

           for x in xrange(0,kbps/10):
                print "\b#",
           print kbps, "kbps"

           time.sleep(1)

if __name__ == "__main__":
     main()

