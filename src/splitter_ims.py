# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucía
# through the Proyecto Motriz "Codificación de Vídeo Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

from __future__ import print_function
import sys,os
import socket
import threading
import struct
from color import Color
import common
import time
from _print_ import _print_

# }}}

# IMS: IP Multicast Set of rules.
class Splitter_IMS(threading.Thread):
    # {{{

    # {{{ Class "constants"

    # {{{ The buffer_size (in chunks). The buffer_size should be
    # proportional to the bit-rate (remember that the latency is also
    # proportional to the buffer_size).
    # }}}
    BUFFER_SIZE = 256

    # {{{ Channel served by the streaming source.
    # }}}
    #CHANNEL = "BBB-134.ogv"
    CHANNEL = ""

    # {{{ The chunk_size (in bytes) depends mainly on the network
    # technology and should be selected as big as possible, depending
    # on the MTU and the bit-error rate.
    # }}}
    CHUNK_SIZE = 1024

    # {{{ Number of chunks of the header.
    # }}}
    HEADER_SIZE = 10

    # {{{ The unicast IP address of the splitter server.
    # }}}
    #SPLITTER_ADDR = "127.0.0.1" # No por ahora
    
    # {{{ Port used to serve the peers (listening port).
    # }}}
    PORT = 4552

    # {{{ The host where the streaming server is running.
    # }}}
    SOURCE_ADDR = "127.0.0.1"

    # {{{ Port where the streaming server is listening.
    # }}}
    SOURCE_PORT = 8000

    # {{{ The multicast IP address of the team, used to send the chunks.
    # }}}
    MCAST_ADDR = "224.0.0.1" # All Systems on this subnet
    #MCAST_ADDR = "224.0.0.2"

    # }}}

    def __init__(self):
        # {{{

        threading.Thread.__init__(self)
        sys.stdout.write(Color.yellow)
        print("Using IMS")
        sys.stdout.write(Color.none)

        print("IMS: Buffer size (in chunks) =", self.BUFFER_SIZE)
        print("IMS: Chunk size (in bytes) =", self.CHUNK_SIZE)
        print('IMS: Channel ="', self.CHANNEL, '"')
        print("IMS: Header size (in chunks) =", self.HEADER_SIZE)
        #print("IMS: Splitter address =", self.SPLITTER_ADDR) # No ahora
        print("IMS: Listening (and multicast) port =", self.PORT)
        print("IMS: Source IP address =", self.SOURCE_ADDR)
        print("IMS: Source port =", self.SOURCE_PORT)
        print("IMS: Multicast address =", self.MCAST_ADDR)

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
        
        # }}}

    def send_the_header(self, peer_serve_socket):
        # {{{

        _print_("IMS: Sending a header of", len(self.header), "bytes")
        try:
            peer_serve_socket.sendall(self.header)
        except:
            pass
        
        # }}}

    def send_the_buffer_size(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("IMS: Sending a buffer_size of", self.BUFFER_SIZE, "bytes")
        message = struct.pack("H", socket.htons(self.BUFFER_SIZE))
        try:
            peer_serve_socket.sendall(message)
        except:
            pass
        
        # }}}

    def send_the_chunk_size(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("IMS: Sending a chunk_size of", self.CHUNK_SIZE, "bytes")
        message = struct.pack("H", socket.htons(self.CHUNK_SIZE))
        try:
            peer_serve_socket.sendall(message)
        except:
            pass
        
        # }}}

    def send_the_mcast_channel(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("IMS: Communicating the multicast channel", (self.MCAST_ADDR, self.PORT))
        message = struct.pack("4sH", socket.inet_aton(self.MCAST_ADDR), socket.htons(self.PORT))
        peer_serve_socket.sendall(message)
        
        # }}}

    def send_the_header_size(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("IMS: Communicating the header size", self.HEADER_SIZE)
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
        sys.stdout.write(Color.green)
        print(serve_socket.getsockname(), '\b: IMS: accepted connection from peer', \
              connection[1])
        sys.stdout.write(Color.none)
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
        self.team_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 0)

        try:
            # This does not work in Windows systems !!
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception as e:
            print ("IMS: ", e)
            pass

        try:
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except Exception as e:
            print ("IMS: ", e)
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
        if __debug__:
            try:
                print(self.source_socket.getsockname(), 'IMS: connecting to the source', self.source, '...')
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
            print("IMS: ", e)
            print(Color.red)
            print(self.source_socket.getsockname(), "\b: IMS: unable to connect to the source ", self.source)
            print(Color.none)
            self.source_socket.close()
            os._exit(1)
        if __debug__:
            print(self.source_socket.getsockname(), 'IMS: connected to', self.source)
        self.source_socket.sendall(self.GET_message.encode())
        _print_(self.source_socket.getsockname(), 'IMS: GET_message =', self.GET_message)

        # }}}

    def configure_sockets(self):
        # {{{ setup_peer_connection_socket()

        try:
            self.setup_peer_connection_socket()
        except Exception as e:
            print("IMS: ", e)
            print(Color.red)
            print(self.peer_connection_socket.getsockname(), "\b: IMS: unable to bind the port ", self.PORT)
            print(Color.none)
            sys.exit('')

        # }}}

        # {{{ setup_team_socket()

        try:
            self.setup_team_socket()
        except Exception as e:
            print("IMS: ", e)
            print(self.team_socket.getsockname(), "\b: IMS: unable to bind", (socket.gethostname(), self.PORT))
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
                print("IMS: No data in the server!")
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
            print("IMS: Loaded", len(self.header), "bytes of header")
            #_print_("3: header_load_counter =", self.header_load_counter)

        self.recvfrom_counter += 1
            
        return chunk

        # }}}

    def send_chunk(self, message, destine):
        # {{{

        self.team_socket.sendto(message, destine)

        if __debug__:
            print('IMS: %5d' % self.chunk_number, Color.red, '->', Color.none, destine)
            sys.stdout.flush()

        self.sendto_counter += 1
        
        # }}}

    def receive_the_header(self):
        # {{{

        if __debug__:
            print("IMS: Requesting the stream header ...")

        self.configure_sockets()
        self.request_the_video_from_the_source()
        self.load_the_video_header()

        if __debug__:
            print("IMS: Stream header received!")

        # }}}

    def run(self):
        # {{{

        self.receive_the_header()
        
        print(self.peer_connection_socket.getsockname(), "\b: IMS: waiting for a peer ...")
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
            self.chunk_number = (self.chunk_number + 1) % common.MAX_CHUNK_NUMBER

        # }}}

    # }}}

