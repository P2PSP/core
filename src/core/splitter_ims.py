"""
@package core
splitter_ims module
"""

# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# IMS: IP Multicast Set of rules.

# {{{ Imports

from __future__ import print_function
import sys,os
import socket
import threading
import struct
import time

<<<<<<< HEAD
from . import common
=======
from core.common import Common
>>>>>>> master
from core._print_ import _print_
from core.color import Color

# }}}

def _p_(*args, **kwargs):
    """Colorize the output."""
    if __debug__:
        sys.stdout.write(Common.IMS_COLOR)
        _print_("IMS:", *args)
        sys.stdout.write(Color.none)

class Splitter_IMS(threading.Thread):
    # {{{

    # {{{ Class "constants"

    BUFFER_SIZE = 256              # Buffer size in chunks
    CHANNEL = "test.ogg"           # Default channel
    #CHANNEL = ""
    CHUNK_SIZE = 1024              # Chunk size in bytes (larger than MTU)
    HEADER_SIZE = 10               # Chunks/header
    #SPLITTER_ADDR = "127.0.0.1"
    PORT = 8001                    # Listening port
    SOURCE_ADDR = "127.0.0.1"      # Streaming server's host
    SOURCE_PORT = 8000             # Streaming server's listening port
    MCAST_ADDR = "224.0.0.1"       # All Systems on this subnet
    #MCAST_ADDR = "224.0.0.2"      # Default IP multicast channel
    TTL = 1                        # Time To Live of multicast packets
    
    # }}}

    def __new__(typ, *args, **kwargs):
        # {{{

        if len(args) == 1 and isinstance(args[0], Splitter_IMS):
            # Parameter is a peer instance; extending its class instead of nesting:
            instance = args[0]
            instance.__class__ = typ
            return instance
        else:
            # Use default object creation
            return object.__new__(typ, *args, **kwargs)

        # }}}

    def __init__(self):
        # {{{

        threading.Thread.__init__(self)
        #sys.stdout.write(Color.yellow)
        #print("Using IMS")
        #sys.stdout.write(Color.none)

        _p_("Buffer size (in chunks) =", self.BUFFER_SIZE)
        _p_("Chunk size (in bytes) =", self.CHUNK_SIZE)
        _p_('Channel ="', self.CHANNEL, '"')
        _p_("Header size (in chunks) =", self.HEADER_SIZE)
        #print("IMS: Splitter address =", self.SPLITTER_ADDR) # No ahora
        _p_("Listening (and multicast) port =", self.PORT)
        _p_("Source IP address =", self.SOURCE_ADDR)
        _p_("Source port =", self.SOURCE_PORT)
        _p_("Multicast address =", self.MCAST_ADDR)

        # {{{ An IMS splitter runs 2 threads. The main one serves the
        # chunks to the team. The other controls peer arrivals. This
        # variable is true while the player is receiving data.
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

        # {{{ Used to talk to the source
        # }}}
        self.source_socket = ""

        # {{{ The video header.
        # }}}
        #self.header = buffer('')

        # {{{ Some other useful definitions.
        # }}}
        self.source = (self.SOURCE_ADDR, self.SOURCE_PORT)
        self.GET_message = 'GET /' + self.CHANNEL + ' HTTP/1.1\r\n'
        self.GET_message += '\r\n'
        self.chunk_number_format = "H"
        self.mcast_channel = (self.MCAST_ADDR, self.PORT)

        self.recvfrom_counter = 0
        self.sendto_counter = 0

        self.header_load_counter = 0

        _p_("Initialized")

        # }}}

    def send_the_header(self, peer_serve_socket):
        # {{{

        _p_("Sending a header of", len(self.header), "bytes")
        try:
            peer_serve_socket.sendall(self.header)
        except:
            pass

        # }}}

    def send_the_buffer_size(self, peer_serve_socket):
        # {{{

        _p_("Sending a buffer_size of", self.BUFFER_SIZE, "bytes")
        message = struct.pack("H", socket.htons(self.BUFFER_SIZE))
        try:
            peer_serve_socket.sendall(message)
        except:
            pass

        # }}}

    def send_the_chunk_size(self, peer_serve_socket):
        # {{{

        _p_("Sending a chunk_size of", self.CHUNK_SIZE, "bytes")
        message = struct.pack("H", socket.htons(self.CHUNK_SIZE))
        try:
            peer_serve_socket.sendall(message)
        except:
            pass

        # }}}

    def send_the_mcast_channel(self, peer_serve_socket):
        # {{{

        _p_("Communicating the multicast channel", (self.MCAST_ADDR, self.PORT))
        message = struct.pack("4sH", socket.inet_aton(self.MCAST_ADDR), socket.htons(self.PORT))
        peer_serve_socket.sendall(message)

        # }}}

    def send_the_header_size(self, peer_serve_socket):
        # {{{

        _p_("Communicating the header size", self.HEADER_SIZE)
        message = struct.pack("H", socket.htons(self.HEADER_SIZE))
        try:
            peer_serve_socket.sendall(message)
        except:
            pass

        # }}}

    def send_configuration(self, sock):
        # {{{

        self.send_the_mcast_channel(sock)
        self.send_the_header_size(sock)
        self.send_the_chunk_size(sock)
        self.send_the_header(sock)
        self.send_the_buffer_size(sock)

        # }}}

    def handle_a_peer_arrival(self, connection):
        # {{{ Handle the arrival of a peer. When a peer want to join a
        # team, first it must establish a TCP connection with the
        # splitter.

        serve_socket = connection[0]
        #sys.stdout.write(Color.green)
        _p_(serve_socket.getsockname(), '\b: IMS: accepted connection from peer', \
              connection[1])
        #sys.stdout.write(Color.none)
        self.send_configuration(serve_socket)
        serve_socket.close()

        # }}}

    def handle_arrivals(self):
        # {{{

        while self.alive:
            peer_serve_socket, peer = self.peer_connection_socket.accept()
            threading.Thread(target=self.handle_a_peer_arrival, args=((peer_serve_socket, peer), )).start()

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
            #self.peer_connection_socket.bind((socket.gethostname(), self.PORT))
            self.peer_connection_socket.bind(('', self.PORT))
        except: # Falta averiguar excepcion
            raise

        # {{{ Set the connection queue to the max!
        # }}}
        self.peer_connection_socket.listen(socket.SOMAXCONN)

        # }}}

    def setup_team_socket(self):
        # {{{ Used to talk with the peers of the team. In this case,
        # it corresponds to a multicast channel.

        self.team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.team_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.TTL)

        try:
            # This does not work in Windows systems !!
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception as e:
            _p_(e)
            pass

        try:
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except Exception as e:
            _p_(e)
            pass

        #try:
            #self.team_socket.bind((socket.gethostname(), self.PORT))
            #self.team_socket.bind(('', self.PORT))
        #except:
            #raise

        # }}}

    def request_the_video_from_the_source(self):
        # {{{ Request the video using HTTP from the source node (Icecast).

        self.source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            _p_(self.source_socket.getsockname(), 'connecting to the source', self.source, '...')
        except Exception as e:
            pass
            # The behavior and return value for calling socket.socket.getsockname() on
            # an unconnected unbound socket is unspecified.
            # On UNIX, it returns an address ('0.0.0.0', 0), while on Windows it raises an obscure exception
            # "error: (10022, 'Invalid argument')"

            # I think we can avoid printing before connecting to the source to prevent errors in windows

        try:
            self.source_socket.connect(self.source)
        except socket.error as e:
            _p_(e)
            #print(Color.red)
            _p_(self.source_socket.getsockname(), "\b: unable to connect to the source ", self.source)
            #print(Color.none)
            self.source_socket.close()
            os._exit(1)
        _p_(self.source_socket.getsockname(), 'connected to', self.source)
        self.source_socket.sendall(self.GET_message.encode())
        _p_(self.source_socket.getsockname(), 'IMS: GET_message =', self.GET_message)

        # }}}

    def configure_sockets(self):
        # {{{ setup_peer_connection_socket()

        try:
            self.setup_peer_connection_socket()
        except Exception as e:
            _p_(e)
            #print(Color.red)
            _p_(self.peer_connection_socket.getsockname(), "\b: unable to bind the port ", self.PORT)
            #print(Color.none)
            sys.exit('')

        # }}}

        # {{{ setup_team_socket()

        try:
            self.setup_team_socket()
        except Exception as e:
            _p_(e)
            _p_(self.team_socket.getsockname(), "\b: unable to bind", (socket.gethostname(), self.PORT))
            sys.exit('')

        # }}}

    def load_the_video_header(self):
        # {{{ Load the video header.

        self.header = b''
        for i in range(self.HEADER_SIZE):
            self.header += self.receive_next_chunk()

        # }}}

    def receive_next_chunk(self):
        # {{{

        chunk = self.source_socket.recv(self.CHUNK_SIZE)
        prev_size = 0
        while len(chunk) < self.CHUNK_SIZE:
            if len(chunk) == prev_size:
                # This section of code is reached when the streaming
                # server (Icecast) finishes a stream and starts with
                # the following one.
                _p_("No data in the server!")
                sys.stdout.flush()
                self.source_socket.close()
                time.sleep(1)
                self.source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.source_socket.connect(self.source)
                self.source_socket.sendall(self.GET_message.encode())
                self.header = b""
                self.header_load_counter = self.HEADER_SIZE
                #_print_("1: header_load_counter =", self.header_load_counter)
                chunk = b""
            prev_size = len(chunk)
            chunk += self.source_socket.recv(self.CHUNK_SIZE - len(chunk))
        return chunk

        # }}}

    def receive_chunk(self):
        # {{{

        chunk = self.receive_next_chunk()
        #_print_ ("2: header_load_counter =", self.header_load_counter)
        if self.header_load_counter > 0:
            self.header += chunk
            self.header_load_counter -= 1
            _p_("Loaded", len(self.header), "bytes of header")
            #_print_("3: header_load_counter =", self.header_load_counter)

        self.recvfrom_counter += 1

        return chunk

        # }}}

    def send_chunk(self, message, destination):
        # {{{

        self.team_socket.sendto(message, destination)

        _p_('%5d' % self.chunk_number, '->', destination)
        sys.stdout.flush()

        self.sendto_counter += 1

        # }}}

    def receive_the_header(self):
        # {{{

        _p_("Requesting the stream header ...")

        self.configure_sockets()
        self.request_the_video_from_the_source()
        self.load_the_video_header()

        _p_("Stream header received!")

        # }}}

    def run(self):
        # {{{

        self.receive_the_header()

        _p_(self.peer_connection_socket.getsockname(), "\b: waiting for a peer ...")
        self.handle_a_peer_arrival(self.peer_connection_socket.accept())
        threading.Thread(target=self.handle_arrivals).start()

        message_format = self.chunk_number_format + str(self.CHUNK_SIZE) + "s"

        #_print_("4: header_load_counter =", self.header_load_counter)
        while self.alive:
            #self.receive_and_send_a_chunk(header_load_counter)
            chunk = self.receive_chunk()
            message = struct.pack(message_format, socket.htons(self.chunk_number), chunk)
            #self.send_chunk(self.receive_chunk(header_load_counter), self.mcast_channel)
            self.send_chunk(message, self.mcast_channel)
            self.chunk_number = (self.chunk_number + 1) % Common.MAX_CHUNK_NUMBER

        # }}}

    # }}}
