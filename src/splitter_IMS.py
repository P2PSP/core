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

# This code implements the IMS splitter side of the P2PSP.

# {{{ Imports

from __future__ import print_function
import time
import sys
import socket
import threading
import struct
import argparse
from color import Color
import common

# }}}

# Some useful definitions.
ADDR = 0
PORT = 1

# IP Multicast Set of Rules
class Splitter_IMS(threading.Thread):
    # {{{

    # {{{ Class "constants"

    # {{{
    # The buffer_size (in chunks) depends on the stream bit-rate and
    # the maximun latency bearable by the users, and must be
    # transmitted to the peers because all peers should use the same
    # buffer_size. Notice that the buffer_size should be proportional
    # to the bit-rate and the latency is proportional to the
    # buffer_size.
    # }}}
    BUFFER_SIZE = 256

    # {{{ Channel served by the streaming source.
    # }}}
    CHANNEL = "Big_Buck_Bunny_small.ogv"

    # {{{
    # The chunk_size depends mainly on the network technology and
    # should be selected as big as possible, depending on the MTU and
    # the bit-error rate.
    # }}}
    CHUNK_SIZE = 1024

    # {{{ Number of chunks of the header.
    # }}}
    HEADER_SIZE = 10

    # {{{ The unicast IP address of the splitter server.
    # }}}
    #SPLITTER_ADDR = "localhost"
    
    # {{{ Port used to serve the peers (listening port).
    # }}}
    PORT = 4552

    # {{{ The host where the streaming server is running.
    # }}}
    SOURCE_ADDR = "localhost"

    # {{{ Port where the streaming server is listening.
    # }}}
    SOURCE_PORT = 8000

    # {{{ The multicast IP address of the team, used to send the chunks.
    # }}}
    #TEAM_ADDR = "224.0.0.1" # All Systems on this Subnet
    #TEAM_ADDR = "224.1.1.1"
    #MCAST_GRP = "224.0.0.1"
    #MCAST_GRP = '224.1.1.1'
    MCAST_ADDR = "224.0.0.1" # All Systems on this subnet

    # {{{ Port used in the multicast group.
    # }}}
    #TEAM_PORT = 4552
    #TEAM_PORT = 8888

    # }}}

    def __init__(self):
        # {{{

        threading.Thread.__init__(self)

        print("Running in", end=' ')
        if __debug__:
            print("debug mode")
        else:
            print("release mode")

        self.print_modulename()
        print("Buffer size (chunks) =", self.BUFFER_SIZE)
        print("Chunk size (bytes) =", self.CHUNK_SIZE)
        print("Channel =", self.CHANNEL)
        print("Header size (chunks) =", self.CHANNEL)
        #print("Splitter address =", self.SPLITTER_ADDR)
        print("Listening and serving port =", self.PORT)
        print("Source IP address =", self.SOURCE_ADDR)
        print("Source port =", self.SOURCE_PORT)
        print("Multicast address =", self.MCAST_ADDR)
        #print("Team multicast port =", self.TEAM_PORT)

        # {{{ A IMS splitter runs 2 threads. The first one controls
        # the peer arrivals. The second one shows some information
        # about the transmission. This variable is used to stop the
        # child threads. They will be alive only while the main thread
        # is alive.
        # }}}
        self.alive = True

        # {{{ Number of the served chunk.
        # }}}
        self.chunk_number = 0

        # {{{ Used to listen to the incomming peers.
        # }}}
        self.peer_connection_socket = ""

        # {{{ Used to listen the team messages.
        # }}}
        self.team_socket = ""

        # {{{ The video header.
        # }}}
        self.header = ""

        # {{{ Some useful definitions.
        # }}}
        self.source = (self.SOURCE_ADDR, self.SOURCE_PORT)
        self.GET_message = 'GET /' + self.CHANNEL + ' HTTP/1.1\r\n'
        self.GET_message += '\r\n'
        self.chunk_format_string = "H" + str(self.CHUNK_SIZE) + "s" # "H1024s
        self.multicast_channel = (self.MCAST_ADDR, self.PORT)
        # }}}

    def print_modulename(self):
        # {{{

        sys.stdout.write(Color.yellow)
        print("Splitter IMS")
        sys.stdout.write(Color.none)

        # }}}

    def send_header(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("Sending a header of", len(self.header), "bytes")
        peer_serve_socket.sendall(self.header)

        # }}}

    def send_buffersize(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("Sending a buffer_size of", self.BUFFER_SIZE, "bytes")
        message = struct.pack("H", socket.htons(self.BUFFER_SIZE))
        peer_serve_socket.sendall(message)

        # }}}

    def send_chunksize(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("Sending a chunk_size of", self.CHUNK_SIZE, "bytes")
        message = struct.pack("H", socket.htons(self.CHUNK_SIZE))
        peer_serve_socket.sendall(message)

        # }}}

    def send_mcast_channel(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("Communicating the multicast channel", (self.MCAST_ADDR, self.PORT))
        message = struct.pack("4sH", socket.inet_aton(self.MCAST_ADDR), socket.htons(self.PORT))
        peer_serve_socket.sendall(message)

        # }}}

        # Ojo, primero transmitimos el canal multicast. Si éste es
        # distinto de 0.0.0.0, se transmite si es un monitor (el peer
        # sería del tipo DBS) o no (sería del tipo IMS).
        
    def handle_peer_arrival(self, connection):
        # {{{ Handle the arrival of a peer. When a peer want to join a
        # team, first it must establish a TCP connection with the
        # splitter.
        sys.stdout.write(Color.green)
        print(peer_serve_socket.getsockname(), '\b: accepted connection from peer', peer)
        self.send_mcast_channel(peer_serve_socket)
        self.send_chunksize(peer_serve_socket)
        self.send_header(peer_serve_socket)
        self.send_buffersize(peer_serve_socket)
        peer_serve_socket.close()
        #self.append_peer(peer)
        sys.stdout.write(Color.none)

        # }}}

    def handle_arrivals(self):
        # {{{ 

        while self.alive:
            peer_serve_socket, peer = self.peer_connection_socket.accept()
            threading.Thread(target=self.handle_peer_arrival, args=((peer_serve_socket, peer), )).start()

        # }}}

    def setup_peer_connection_socket(self):
        # {{{ Used to listen to the incomming peers.

        self.peer_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # This does not work in Windows systems.
            self.peer_connection_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except: # Falta averiguar excepcion
            pass

        try:
            self.peer_connection_socket.bind((socket.gethostname(), self.PORT))
        except: # Falta averiguar excepcion
            raise

        # {{{ Set the connection queue to the max!
        # }}}
        self.peer_connection_socket.listen(socket.SOMAXCONN) 

        # }}}

    def setup_team_socket(self):
        # {{{ Used to talk with the peers of the team. In this case,
        # it corresponds to a multicast channel.
        
        #self.team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
        self.team_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        try:
            # This does not work in Windows systems !!
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass
        try:
            self.team_socket.bind((socket.gethostname(), self.PORT))
        except:
            raise

        # }}}

    def request_video(self):
        # {{{ Request the video using HTTP from the source node (Icecast).

        source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if __debug__:
            print(source_socket.getsockname(), 'connecting to the source', self.source, '...')
        source_socket.connect(self.source)
        if __debug__:
            print(source_socket.getsockname(), 'connected to', self.source)
        source_socket.sendall(self.GET_message)
        if __debug__:
            print(source_socket.getsockname(), 'GET_message =', self.GET_message)
        return source_socket

        # }}}

    def receive_next_chunk(self, sock, header_length):
        # {{{

        data = sock.recv(self.CHUNK_SIZE)
        prev_size = 0
        while len(data) < self.CHUNK_SIZE:
            if len(data) == prev_size:
                # This section of code is reached when the streaming
                # server (Icecast) finishes a stream and starts with
                # the following one.
                print('?', end='')
                sys.stdout.flush()
                #time.sleep(1)
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(self.source)
                sock.sendall(self.GET_message)
                self.header = ""
                header_length = self.HEADER_SIZE
                data = ""
            prev_size = len(data)
            data += sock.recv(self.CHUNK_SIZE - len(data))
        return data, sock, header_length

        # }}}

    def run(self):
        # {{{

        # {{{ setup_peer_connection_socket()

        try:
            self.setup_peer_connection_socket()
        except Exception, e:
            print(e)
            print(self.peer_connection_socket.getsockname(), "\b: unable to bind", (self.SPLITTER_ADDR, self.SPLITTER_PORT))
            sys.exit('')

        # }}}

        # {{{ setup_team_socket()

        try:
            self.setup_team_socket()
        except Exception, e:
            print(e)
            print(self.team_socket.getsockname(), "\b: unable to bind", (socket.gethostname(), self.PORT))
            sys.exit('')

        # }}}

        source_socket = self.request_video()

        # {{{ Load the video header.

        for i in xrange(self.HEADER_SIZE):
            self.header += self.receive_next_chunk(source_socket, 0)[0]

        # }}}

        print(self.peer_connection_socket.getsockname(), "\b: waiting for the monitor peer ...")
        self.handle_peer_arrival(self.peer_connection_socket.accept())
        threading.Thread(target=self.handle_arrivals).start()

        header_length = 0

        while self.alive:
            # Receive data from the source
            chunk, source_socket, header_length = self.receive_next_chunk(source_socket, header_length)

            if header_length > 0:
                print("Header length =", header_length)
                self.header += chunk
                header_length -= 1

            message = struct.pack(self.chunk_format_string, socket.htons(self.chunk_number), chunk)
            self.team_socket.sendto(message, self.multicast_channel)

            if __debug__:
                print('%5d' % self.chunk_number, Color.red, '->', Color.none, self.multicast_channel)
                sys.stdout.flush()

            self.chunk_number = (self.chunk_number + 1) % common.MAX_CHUNK_NUMBER

        # }}}

    # }}}

